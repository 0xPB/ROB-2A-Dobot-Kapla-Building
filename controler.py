from serial.tools import list_ports
from dobot_extensions import Dobot
from pydobot.dobot import MODE_PTP
import numpy
import time
import sys, argparse, math
import pickle

MAX_RAIL_DISTANCE = -500

class Pose (object):
    """x, y, z, r dans le repère du bras, g la position du rail """
    def __init__(self, x=0, y=0, z=0, r=0, g=0 , pose=None):
        if pose is None :
            #print("new pose")
            self.x = x
            self.y = y
            self.z = z
            self.r = r
            self.g = g
        else:
            #print("copy pose")
            self.x = pose.x
            self.y = pose.y
            self.z = pose.z
            self.r = pose.r
            self.g = pose.g

    def get_arm_pos(self):
        return self.x, self.y, self.z, self.r

    def get_rail_pos(self):
        return self.g
    def short_repr(self):
        return (f"x:{self.x}, y:{self.y}, z:{self.z} "+
                f"r:{self.r}, g:{self.g}")


    def __eq__(self, pose):
        dx = abs(self.x - pose.x)
        dy = abs(self.y - pose.y)
        dz = abs(self.z - pose.z)
        dr = abs(self.r - pose.r)
        dg = abs(self.g - pose.g)
        liste_delta = [dx, dy, dr, dz, dg]
        for i in liste_delta:
            if i > 3:
                return False
        return True
    def return_delta(self, pose):
            dx = self.x - pose.x
            dy = self.y - pose.y
            dz = self.z - pose.z
            dr = self.r - pose.r
            dg = self.g - pose.g
            return [dx, dy , dz, dr, dg]

    def __repr__(self):
        return (f"Robot :\n   x -> {self.x} \n   y -> {self.y} \n   z -> {self.z} \n   "+
                f"r -> {self.r} \nRail :\n   g -> {self.g} \n")


class Data:
    def __init__(self, pose = Pose(), file = "file"):
        self.actual_pose = pose
        self.save_pose = dict()
        self.file = file

    def add_save_pose(self, name, pose, description = "not defined"):
        self.save_pose[name] = (pose, description)

    def save(self):
        with open(self.file, "wb") as f:
            pickle.dump(self, f)

    def load(self):
        with open(self.file, "rb") as f:
            return pickle.load(f)

    def __repr__(self):
        str_return = f"ACTUAL POSE :\n{self.actual_pose}"
        str_return += f"\nSAVED POSE :\n"
        for name,i in self.save_pose.items():
            str_return += f"Name: {name}\nDescription: \n   {i[1]}\n{i[0]} "
            str_return += f"____________________ \n"
        return str_return



class Pydobot:

    max_z = 100

    # 0 pas d'init, 1 init bras rail, 2 init rail, 3 init bras, 
    def __init__(self, port, go_home=True, load_save=False, data=Data(),file="save.pdbt"):
        print(f"settings --> {go_home}, {load_save}")
        self.port = port
        self.rail_pos = 0
        self.go_home = go_home
        self.load_save = load_save
        self.file = file
        self.suck = False

        # Settings
        

    def __enter__(self):
        print("-- Connecting to the dobot..")
        print(f"setting --> {self.go_home}, {self.load_save}")
        self.device = Dobot(port=self.port)
        self.device.suck(False)

        if self.go_home > 0:

            if self.go_home == 1 or self.go_home == 3:
                print("-- arm initialization..")
                p = self.get_pose()
                p.z += 100
                self.go_to_pose(p, mode=MODE_PTP.MOVJ_XYZ)
                self.device.wait_for_cmd(self.device.home())
                self.home = self.get_pose()

            if self.go_home < 3:
                print("-- rail initialization..  ", end=" ")
                self.device.conveyor_belt(int(40), interface = 0, direction=1)
                input("Press for Stop")
                self.device.conveyor_belt(0, interface=0, direction=1)

        if self.load_save == 1:
            print("-- loading data")
            with open(self.file, "rb") as f:
                self.data = pickle.load(f)

            if self.go_home == 3 or self.go_home == 0:
                self.rail_pos = self.data.actual_pose.g

        else:
            print("-- creation of new data")
            self.data = Data(self.get_pose(), self.file)


        print("-- initialization completed")
        return self

    def __exit__(self, *arg):
        print("-- save")
        self.data.actual_pose = self.get_pose()
        with open(self.file, "wb") as f:
            pickle.dump(self.data, f)
        self.device.close()


    def toggle_suck(self):
        print(f"suction {'activated' if self.suck else 'disabled'} ")
        self.suck = not self.suck
        self.device.suck(self.suck)

    def rail_mouv_distance(self, distance, direction, speed=40, wait=True):
        futur_belt_pos = distance*direction + self.rail_pos
        if futur_belt_pos < MAX_RAIL_DISTANCE:
            distance = self.rail_pos - MAX_RAIL_DISTANCE
        elif futur_belt_pos > 0:
            distance = -self.rail_pos
        try:
            self.device.wait_for_cmd(self.device.conveyor_belt_distance(speed, distance, direction))
        except Exception as err:
            pass
        if wait:
            time.sleep(distance/30)
        self.rail_pos += distance*direction

    def rail_mouv_pos(self, pos, speed=40, wait=True):
        distance = abs(pos - self.rail_pos)
        direction = 1 if pos > self.rail_pos else -1
        self.rail_mouv_distance(distance, direction, speed, wait)

    def get_pose(self):
        pose = self.device.get_pose().position
        p = Pose(pose.x, pose.y, pose.z, pose.r, self.rail_pos)
        return p


    def pick(self, pose, up=40,reset_rot=False ,rot=0):
        pose = Pose(pose=pose)
        pose_ = self.get_pose()
        pose_.z = self.max_z
        self.go_to_pose(pose_)

        pose.z += up
        print("go pose 1")
        self.go_to_pose(pose)
        if reset_rot:
            pose.r = 0
            self.go_to_pose(pose, mode=MODE_PTP.MOVJ_XYZ)
        if rot != 0:
            pose.r += rot
            self.go_to_pose(pose, mode=MODE_PTP.MOVJ_XYZ)
        pose.z -= up
        print("go pose 2")
        self.go_to_pose(pose)
        self.toggle_suck()
        time.sleep(0.2)
        pose.z += up
        print("go pose 3")
        self.go_to_pose(pose)
        pose.z -= up

    def mouv_z(self, distance=None):
        if distance == None:
            p = self.get_pose()
            p.z = self.max_z
            self.go_to_pose(p)
        else:
            p = self.get_pose()
            p.z += distance
            self.go_to_pose(p)


    def save_pose(self, name, description="not defined"):
        self.data.add_save_pose(name, self.get_pose(), description)

    def go_to_pose(self, pose, mode=MODE_PTP.MOVL_XYZ):
        if type(pose) == type("aa"):
            print("-- load 1")        
            if pose in self.data.save_pose:
                print("-- load data pose")
                pose = self.data.save_pose[pose][0]

        print(f"Movement to position {pose.short_repr()}")
        self.rail_mouv_pos(pose.get_rail_pos())
        self.device.move_to(*pose.get_arm_pos()[:-1], r=pose.get_arm_pos()[-1], mode=mode)
        i = 0
        while pose != self.get_pose():
            i += 1
            if i > 3:
                print("pose impossible")
                print(self.get_pose().short_repr())
                print(pose.short_repr())

                delta = pose.return_delta(self.get_pose())
                if i < 5 : 
                    pose.z -= delta[2]
                elif i < 8 :
                    pose.x -= delta[0] 
                elif i < 10 :
                    pose.y -= delta[1]
                elif i < 12:
                    self.device.wait_for_cmd(self.device.home())
                    
                
                mode = MODE_PTP.MOVJ_XYZ

            self.device.move_to(*pose.get_arm_pos()[:-1], r=pose.get_arm_pos()[-1], mode=mode)
            time.sleep(1)

    def learn_mouv(self):
        self.save_pose = list()
        while wrt := "":
            self.save_pose.append(self.device.get_pose())
            wrt = input("continue")

    def repeat_mouv(self):
        for i in self.save_pose:
            self.device.move_to(i.position.x, i.position.y, i.position.z, i.position.r)
            input("continue")



