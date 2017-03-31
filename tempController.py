# -*- coding: utf-8 -*-
"""
Created on Tue Mar 28 20:37:36 2017

@author: Mok Jun Neng
"""

import RPi.GPIO as GPIO
from libdw import sm



GPIO.setmode(GPIO.BCM)

sensorPIN = 4

GPIO.setup(sensorPIN, GPIO.IN, GPIO.PUD_DOWN)
GPIO.setup(12, GPIO.OUT)

pump = GPIO.PWM(12, frequency)
fan = GPIO.PWM(13, frequency)
pump.start(1)
fan.start(1)



import os
import glob
import time
 
os.system('modprobe w1-gpio')
os.system('modprobe w1-therm')
 
base_dir = '/sys/bus/w1/devices/'
device_folder = glob.glob(base_dir + '28*')[0]
device_file = device_folder + '/w1_slave'
 
def read_temp_raw():
    f = open(device_file, 'r')
    lines = f.readlines()
    f.close()
    return lines
 
def read_temp():
    lines = read_temp_raw()
    while lines[0].strip()[-3:] != 'YES':
        time.sleep(0.2)
        lines = read_temp_raw()
    equals_pos = lines[1].find('t=')
    if equals_pos != -1:
        temp_string = lines[1][equals_pos+2:]
        temp_c = float(temp_string) / 1000.0
        temp_f = temp_c * 9.0 / 5.0 + 32.0
        return temp_c, temp_f

deg_c, deg_f = read_temp()
	
while True:
	print(read_temp())	
	time.sleep(1)

class temp_controller(sm.SM):
    
    startState = 0
    def getNextValues(self,state,inp):
        if sensorValue > target_temperature:
            return 1, (0.5,0.5)
        else:
            return 0, (0,0)

outp = temp_controller()
outp.start()

while True:
    out = outp.step(sensorValue)
    pump.ChangeDutyCycle(out[0])
    fan.ChangeDutyCycle(out[1])
        
        
        
        


