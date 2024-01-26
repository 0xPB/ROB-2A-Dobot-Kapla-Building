import pygame
from pygame.locals import *
import json
import numpy as np
from math import cos, sin, sqrt
import time
tailleMap = (800,800)

def read_json(file):
    with open('construction.json', "rb") as json_data:
        kapla_list = json.load(json_data)
        data = sorted(kapla_list, key=lambda b: (b["base"][2], b["base"][1], b["base"][0]))
    return data

pygame.init()
fenetre = pygame.display.set_mode(tailleMap)
pygame.key.set_repeat(1, 30)


instructions = read_json("construction.json")
print(*instructions, sep="\n")


multipli = 3
décal = 70
taille_kaple = sqrt((25/2)**2+(25/2)**2)*multipli

wait = 1

while 1:
    pygame.draw.rect(fenetre, (0, 0, 0), (0, 0, *(tailleMap)), 8000)
    

    for instruction in instructions[:]:
        pos = (np.array((*instruction["base"][:2],*instruction["attitude"][:2]))+ 
               np.array((décal,décal,0,0))) * np.array((multipli
                                                    ,multipli
                                                    ,multipli
                                                    ,multipli
                                                    ))
        pygame.draw.rect(fenetre, (instruction["attitude"][2]*2+100, instruction["attitude"][2]*2+100, instruction["attitude"][2]*2+100), (pos), 2)


        pivot = np.radians(instruction["pivot"]) + np.radians(45)
        pos[0] += taille_kaple*cos(pivot)
        pos[1] += taille_kaple*sin(pivot)

        pygame.draw.circle(fenetre, (255,255,255), pos[:2], 3)
        if wait:
            pygame.display.flip()
            time.sleep(1)
            for event in pygame.event.get():
                if event.type == QUIT:
                    pygame.quit()
                    break
            continue

    pygame.display.flip()
    for event in pygame.event.get():
                if event.type == QUIT:
                    pygame.quit()
                    break