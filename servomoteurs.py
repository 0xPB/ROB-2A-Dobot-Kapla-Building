import RPi.GPIO as GPIO
from time import sleep

#variables positions
pos_vert = 11.5

#port
port = 12

#fonction pour l'angle
def servo_vert():
    pwm.ChangeDutyCycle(6.8)
    sleep(1)


def servo_hori():

    for i in range(0,500, 20):
        pwm.ChangeDutyCycle(7+i/100)
        sleep(0.05)
    #pwm.ChangeDutyCycle(10)
    
    #pwm.ChangeDutyCycle(11.5)
    #sleep(1)

GPIO.setmode(GPIO.BOARD)
GPIO.setup(12, GPIO.OUT)
GPIO.setwarnings(False)
pwm = GPIO.PWM(12,50)
pwm.start(0)

#aller en pos horizontale
servo_hori()

#aller en pos verticale
servo_vert()
