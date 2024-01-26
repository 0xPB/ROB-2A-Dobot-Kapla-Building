from serial.tools import list_ports
from dobot_extensions import Dobot
from pydobot.dobot import MODE_PTP
import numpy as np
import time
import sys, argparse
from controler import Pydobot, Pose, Data
import json
from math import cos, sin, sqrt

import RPi.GPIO as GPIO


port = '/dev/ttyUSB0'

parser = argparse.ArgumentParser(description="set dobot launch mode")
parser.add_argument('-s', '--sethome', type=int, required=False,
                    help='0 - no initialization, 1 - arm and rail initialization, 2 - rail initialization, 3 - arm initialization')
parser.add_argument('-l', '--load', type=int, required=False,
                    help='0 - creating new backup, 1 - loading backup')
args = parser.parse_args()


def servo_vert():
    GPIO.setmode(GPIO.BOARD)
    GPIO.setup(12, GPIO.OUT)
    GPIO.setwarnings(False)
    pwm = GPIO.PWM(12,50)
    pwm.start(0)
    pwm.ChangeDutyCycle(6.8)
    time.sleep(1)
    pwm.stop()
    GPIO.cleanup()


def servo_hori():
    GPIO.setmode(GPIO.BOARD)
    GPIO.setup(12, GPIO.OUT)
    GPIO.setwarnings(False)
    pwm = GPIO.PWM(12,50)
    pwm.start(0)
    for i in range(0,500, 20):
        pwm.ChangeDutyCycle(7+i/100)
        time.sleep(0.05)
    pwm.stop()
    GPIO.cleanup()

def setup():
    GPIO.setmode(GPIO.BOARD)
    GPIO.setup(12, GPIO.OUT)
    GPIO.setwarnings(False)
    pwm = GPIO.PWM(12,50)
    pwm.start(0)
    return pwm


def pick_in_magasin(pose):
    for i in range(8):
        pose = Pose(pose=pose)
        pose.y += 2
        pose.x += 2
        pose.z -= 1
        for j in range(4):
            for i in range(3):
                yield pose
                pose.x -= 20
                pose.z -= 0.7
            pose.x += 20*3
            pose.y -= 20

def read_json(file):
    with open('construction.json', "rb") as json_data:
        kapla_list = json.load(json_data)
        data = sorted(kapla_list, key=lambda b: (b["base"][2], b["base"][1], b["base"][0]))
    return data

def build(instructions, build_pose, pivot_sup=0):
    taille_kaple = sqrt((25/2)**2+(25/2)**2)

    for instruction in instructions:
        
        return_pose = Pose(pose=build_pose)

        if instruction["attitude"][0] == 70:
            return_pose.r += 90
        return_pose.r -= instruction["pivot"]

        pivot = np.radians(instruction["pivot"]) + np.radians(45)+ pivot_sup
        return_pose.x += instruction["base"][0] + taille_kaple*cos(pivot)
        return_pose.y -= instruction["base"][1] - taille_kaple*sin(pivot)
        
        return_pose.z += instruction["base"][2] + instruction["attitude"][2]
        print(return_pose)

        yield return_pose


def turn_kapla(instruction, turn_pose):
    """ turn_pose -> (turn_place, turn_pick)"""
    servo_vert()
    pose = Pose(pose=turn_pose[0])
    if instruction["attitude"][2] <= 25:
        rot = 0
        if instruction["attitude"][2] == 20:
            rot = 90
        pose.z += 30
        bot.pick(pose,up =70, rot=rot)
        time.sleep(3)

        servo_hori()

        pose = Pose(pose=turn_pose[1])
        pose_ = bot.get_pose()
        pose_.z = bot.max_z
        print("go pose 0")
        bot.go_to_pose(pose_)

        print("go pose 0")
        pose.z += 5
        bot.go_to_pose(pose)
        
        pose.r = 0
        print("go pose rot")
        bot.go_to_pose(pose, mode=MODE_PTP.MOVJ_XYZ)

        print("go pose 1")
        pose.z -= 5
        bot.go_to_pose(pose)
        bot.toggle_suck()
        time.sleep(0.2)
        pose.y += 70
        bot.go_to_pose(pose)
        time.sleep(2)

        servo_vert()


def save_pose(name, rail, description="no defined"):
    bot.rail_mouv_pos(rail)
    input(f"select {name}")
    bot.save_pose(name, description)
    bot.mouv_z()

def test():
    p = bot.get_pose()
    for i in range(10):
        bot.pick(p, reset_rot=True)
        bot.pick(p, rot=90)

builds = read_json("construction.json")


with Pydobot(port, args.sethome, args.load) as bot:


    #save_pose("store", -150)
#     servo_hori(pwm)
#     save_pose("poses_return_pick", -400)
#     servo_vert(pwm)
#     save_pose("poses_return_place", -440)
    #save_pose("poses_depose", -300)


    poses_shop = bot.data.save_pose["store"][0]
    poses_return_pick = bot.data.save_pose["poses_return_pick"][0]
    poses_return_place = bot.data.save_pose["poses_return_place"][0]
    poses_depose = bot.data.save_pose["poses_depose"][0]

    poses_depose.r = 0
    poses_shop.r = 0
    poses_return_pick.r = 0
    poses_return_place.r = 0

    poses_return = (poses_return_place,poses_return_pick)
    

    ite_shop = pick_in_magasin(poses_shop)
    ite_depose = build(builds, poses_depose)
    
    for pose_shop, pose_depose, build in zip(ite_shop,ite_depose,builds):

        print(build)
        bot.mouv_z()
        bot.pick(pose_shop, reset_rot=True)
        turn_kapla(build, poses_return)
        #bot.pick(poses_return_pick)
        #bot.pick(poses_return_pick)
        bot.pick(pose_depose)
        bot.mouv_z()








    
    




