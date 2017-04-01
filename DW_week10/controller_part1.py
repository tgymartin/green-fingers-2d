# -*- coding: utf-8 -*-
"""
Created on Tue Mar 28 20:37:36 2017

@author: Mok Jun Neng
"""

import RPi.GPIO as GPIO
from libdw import sm
import os
import glob
import time

### PIN NUMBERS ###
tempPin = 4
motorPin = 12
fanPin = 13

### PARAMETERS ###
targetTemperature = 30.0
pwmFreq = 100

class tempSensor:
    #/sys/bus/w1/devices/28-000008ae29b8/w1_slave
    def __init__(self):
        os.system('modprobe w1-gpio')
        os.system('modprobe w1-therm')
        self.base_dir = '/sys/bus/w1/devices/'
        self.device_folder = glob.glob(self.base_dir + '28*')[0]
        self.device_file = self.device_folder + '/w1_slave'

    def read_temp_raw(self):
        f = open(self.device_file, 'r')
        lines = f.readlines()
        f.close()
        return lines

    def __call__(self):
        lines = self.read_temp_raw()
        while lines[0].strip()[-3:] != 'YES':
            time.sleep(0.2)
            lines = self.read_temp_raw()
        equals_pos = lines[1].find('t=')
        if equals_pos != -1:
            temp_string = lines[1][equals_pos+2:]
            temp_c = float(temp_string) / 1000.0
            return temp_c

class MotorSM(sm.SM):
    startState = 0
    def __init__(self, targetTemperature):
        self.targetTemperature = targetTemperature
    def getNextValues(self,state,inp):
        if inp > self.targetTemperature:
            return 1, (1.0,1.0)
        else:
            return 0, (0,0)

#setup
GPIO.setmode(GPIO.BCM)
GPIO.setup(tempPin, GPIO.IN, GPIO.PUD_UP)
GPIO.setup(motorPin, GPIO.OUT)
GPIO.setup(fanPin, GPIO.OUT)

pump = GPIO.PWM(motorPin, pwmFreq)
pump.start(0.0)
fan = GPIO.PWM(fanPin, pwmFreq)
fan.start(0.0)

#create controller object
motorController = MotorSM(targetTemperature)
motorController.start()

#create sensor object
temp = tempSensor()

def main():
    currentTemp = temp()
    print 'Current temp: %.3f' %(currentTemp)
    controllerOutput = motorController.step(currentTemp)
    pump.ChangeDutyCycle(100*controllerOutput[0])
    fan.ChangeDutyCycle(100*controllerOutput[1])
    time.sleep(0.2)

while True:
    try:
        main()
    except KeyboardInterrupt:
        print 'Cleaning and Exiting...'
        GPIO.cleanup()
        print 'Done'
        exit()