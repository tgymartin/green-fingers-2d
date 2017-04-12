
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
import os
import glob
import time
from PIDsm import PID_ControllerSM

### PIN NUMBERS ###
tempPin = 4
motorPin = 12
fanPin = 13

### PARAMETERS ###
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
targetTemperature = raw_input('Please key in your desired target temperature: ')
motorController = PID_ControllerSM(float(targetTemperature),30,0,10)
motorController.start()
fanController = PID_ControllerSM(float(targetTemperature),30,0,10)
fanController.start()

#create sensor object
temp = tempSensor()

def main(): #main code to loop indefinitely here
    #check current temperature
    currentTemp = temp()
    print 'Current temp: %.3f' %(currentTemp) #for monitoring in the terminal
    motorOutput = motorController.step(currentTemp) #get the amount of PWM to output to fan and pump from the state machine
    fanOutput = fanController.step(currentTemp)
    pump.ChangeDutyCycle(motorOutput) #output the pump PWM. ChangeDutyCycle takes a value from 0 to 100%
    fan.ChangeDutyCycle(fanOutput) #output the fan PWM
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