'''
2D Group Members:
    > Charlotte Phang
    > Lau Wenkie
    > Mok Jun Neng
    > Martin Tan
    > Dicson Candra
'''

#Import relevant modules
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

#Code to read temperature from the ####################### sensor
class tempSensor:
    #Location of file to read from for temperature: /sys/bus/w1/devices/28-000008ae29b8/w1_slave
    #to manually read, "cat /sys/bus/w1/devices/28-000008ae29b8/w1_slave" in terminal
    def __init__(self):
        os.system('modprobe w1-gpio')
        os.system('modprobe w1-therm')
        #define directory of the temperature data in the linux filesystem
        self.base_dir = '/sys/bus/w1/devices/'
        self.device_folder = glob.glob(self.base_dir + '28*')[0]
        self.device_file = self.device_folder + '/w1_slave'

    def read_temp_raw(self): #reading raw output of the 1 wire bus
        f = open(self.device_file, 'r') #open file defined in self.device_file
        lines = f.readlines()
        f.close() #close file to reset the file pointer
        return lines

    def __call__(self): #function to extract temperature data from the raw data in string
        lines = self.read_temp_raw()
        while lines[0].strip()[-3:] != 'YES':
            time.sleep(0.2)
            lines = self.read_temp_raw()
        equals_pos = lines[1].find('t=')
        if equals_pos != -1:
            temp_string = lines[1][equals_pos+2:]
            temp_c = float(temp_string) / 1000.0
            return temp_c

class MotorSM(sm.SM): #state machine to control PWM of pump and fan
    startState = 0
    def __init__(self, targetTemperature):
        self.targetTemperature = targetTemperature
    def getNextValues(self,state,inp):
        if state == 0: #if pump and fan is off
            if inp > self.targetTemperature: #check if the measured temperature higher than the temperature
                state = 1 #if yes, go to state 1
                output = (1.0,1.0) #turn on the pump and fan
                return state, output
            else:
                state = 0 #else the pump and fan remains off
                output = (0.0,0.0)
                return state, output
        elif state == 1: #else if pump and fan is on
            if inp < self.targetTemperature: #check if the temperature has dropped below the set temperature
                state = 0 #go to state 0
                output = (0.0,0.0) #turn off the pump and fan
                return state, output
            else:
                state = 1 #else if target temperature is higher than the set temperature, remain in state 1
                output = (1.0,1.0)
                return state, output

#Set up global variables
GPIO.setmode(GPIO.BCM) #use BCM pin numbering system
GPIO.setup(tempPin, GPIO.IN, GPIO.PUD_UP) #set up the 1 wire interface
GPIO.setup(motorPin, GPIO.OUT) #setup the motor pin
GPIO.setup(fanPin, GPIO.OUT) #setup the fan pin

#define the fan and pump pins as PWM pins and initialise them at 0% PWM (off)
pump = GPIO.PWM(motorPin, pwmFreq) 
pump.start(0.0)
fan = GPIO.PWM(fanPin, pwmFreq)
fan.start(0.0)

#create controller object from MotorSM class
motorController = MotorSM(targetTemperature)
motorController.start()

#create sensor object
temp = tempSensor()

def main(): #main code to loop indefinitely here
    #check current temperature
    currentTemp = temp()
    print 'Current temp: %.3f' %(currentTemp) #for monitoring in the terminal
    controllerOutput = motorController.step(currentTemp) #get the amount of PWM to output to fan and pump from the state machine
    pump.ChangeDutyCycle(100*controllerOutput[0]) #output the pump PWM. ChangeDutyCycle takes a value from 0 to 100%
    fan.ChangeDutyCycle(100*controllerOutput[1]) #output the fan PWM
    time.sleep(0.2) #prevent the code from updating too fast

#####################################################################################
### Run the main code unless user terminates using Ctrl+C.                        ###
### Before exiting, code will reset and release GPIO control to deactivate motor. ###
#####################################################################################
while True:
    try:
        main() #execute main()
    except KeyboardInterrupt:
        print 'Cleaning and Exiting...'
        GPIO.cleanup() #clean up the pins and exit the program
        print 'Done'
        exit()