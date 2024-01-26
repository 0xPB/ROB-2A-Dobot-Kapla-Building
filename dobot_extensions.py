import pydobot
import math
import struct

import serial
import time
from threading import RLock

import platform
from typing import NamedTuple, Set, Optional
import logging

from pydobot.message import Message

PORT_GP1 = 0x00
PORT_GP2 = 0x01
PORT_GP4 = 0x02
PORT_GP5 = 0x03

class Dobot(pydobot.Dobot):
    def conveyor_belt_distance(self, speed_mm_per_sec, distance_mm, direction=1, interface=0):
        if speed_mm_per_sec > 100:
            raise pydobot.dobot.DobotException("Speed must be <= 100 mm/s")

        MM_PER_REV = 34 * math.pi  # Seems to actually be closer to 36mm when measured but 34 works better
        STEP_ANGLE_DEG = 1.8
        STEPS_PER_REV = 360.0 / STEP_ANGLE_DEG * 10.0 * 16.0 / 2.0  # Spec sheet says that it can do 1.8deg increments, no idea what the 10 * 16 / 2 fudge factor is....
        distance_steps = distance_mm / MM_PER_REV * STEPS_PER_REV
        speed_steps_per_sec = speed_mm_per_sec / MM_PER_REV * STEPS_PER_REV * direction
        return self._extract_cmd_index(self._set_stepper_motor_distance(int(speed_steps_per_sec), int(distance_steps), interface))
    
    def conveyor_belt(self, speed_mm_per_sec, direction=1, interface=0):
        if speed_mm_per_sec > 100:
            raise pydobot.dobot.DobotException("Speed must be <= 100 mm/s")

        MM_PER_REV = 34 * math.pi  # Seems to actually be closer to 36mm when measured but 34 works better
        STEP_ANGLE_DEG = 1.8
        STEPS_PER_REV = 360.0 / STEP_ANGLE_DEG * 10.0 * 16.0 / 2.0  # Spec sheet says that it can do 1.8deg increments, no idea what the 10 * 16 / 2 fudge factor is....
        speed_steps_per_sec = speed_mm_per_sec / MM_PER_REV * STEPS_PER_REV * direction
        return self._extract_cmd_index(self._set_stepper_motor(int(speed_steps_per_sec), interface))

    def conveyor_belt(self, speed_mm_per_sec, direction=1, interface=0):
        if speed_mm_per_sec > 100:
            raise pydobot.dobot.DobotException("Speed must be <= 100 mm/s")

        MM_PER_REV = 34 * math.pi  # Seems to actually be closer to 36mm when measured but 34 works better
        STEP_ANGLE_DEG = 1.8
        STEPS_PER_REV = 360.0 / STEP_ANGLE_DEG * 10.0 * 16.0 / 2.0  # Spec sheet says that it can do 1.8deg increments, no idea what the 10 * 16 / 2 fudge factor is....
        speed_steps_per_sec = speed_mm_per_sec / MM_PER_REV * STEPS_PER_REV * direction
        return self._extract_cmd_index(self._set_stepper_motor(int(speed_steps_per_sec), interface))
    


    # capteur photoelectrique      
    def SetInfraredSensor(self, enable=True, infraredPort=PORT_GP4, version=1):
        msg = Message()
        msg.id = 138
        msg.ctrl = 0x01
        msg.params = bytearray([])
        msg.params.extend(bytearray([int(enable)]))
        msg.params.extend(bytearray([infraredPort]))
        msg.params.extend(bytearray([version]))
        self._send_command(msg)


    def GetInfraredSensor(self, infraredPort=PORT_GP4):
        msg = Message()
        msg.id = 138
        msg.ctrl = 0x00
        msg.params = bytearray([])
        msg.params.extend(bytearray([infraredPort]))
        response = self._send_command(msg)
        level = struct.unpack_from('?', response.params, 0)[0]
        return level

        
    def _set_queued_cmd_clear(self):
        msg = Message()
        msg.id = 245
        msg.ctrl = 0x01
        return self._send_command(msg)

    def __init__(self, port: Optional[str] = None) -> None:
        self.logger = logging.Logger(__name__)
        self._lock = RLock()

        if port is None:
            # Find the serial port
            ports = list_ports.comports()
            for thing in ports:
                if thing.vid in (4292, 6790):
                    self.logger.debug(f"Found a com port to talk to DOBOT ({thing}).")
                    port = thing.device
                    break
            else:
                raise DobotException("Device not found!")

        try:
            if platform.system() == 'Windows':
                self._ser = serial.Serial(
                    port,
                    baudrate=115200,
                    parity=serial.PARITY_NONE,
                    stopbits=serial.STOPBITS_ONE,
                    bytesize=serial.EIGHTBITS,
                    timeout=2)
                self._ser.close()
                time.sleep(1)
            self._ser = serial.Serial(
                port,
                baudrate=115200,
                parity=serial.PARITY_NONE,
                stopbits=serial.STOPBITS_ONE,
                bytesize=serial.EIGHTBITS)
            time.sleep(0.5)
                
        except serial.serialutil.SerialException as e:
            raise Exception

        self.logger.debug('pydobot: %s open' % self._ser.name if self._ser.isOpen() else 'failed to open serial port')

        self._set_queued_cmd_start_exec()
        self._set_queued_cmd_clear()
        self._set_ptp_joint_params(200, 200, 200, 200, 200, 200, 200, 200)
        self._set_ptp_coordinate_params(velocity=200, acceleration=200)
        self._set_ptp_jump_params(10, 200)
        self._set_ptp_common_params(velocity=100, acceleration=100)

        alarms = self.get_alarms()

        if alarms:
            self.logger.warning(f"Clearing alarms: {', '.join(map(str, alarms))}.")
            self.clear_alarms()


