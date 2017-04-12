# Part 2.1: Heat Exchanger controller
# Your task is to design the controller:
# Decide what kind of controller you will use? Proportional or Proportional-Derivative controller? Explain your choice.
# What is the gain value you use in your controller? How do you decide on the values of the gains?
# Modify your code in Part 1 to include the controller.

# Part 2.2: Test Program
# Your task to write a GUI application to test your controller state machine. The GUI application must satisfy the following:
# You must use Kivy for your GUI library
# The application allow the user to set the target temperature of the system. Decide what should be the value of this target temperature.
# The application allow the user to change and modify the temperature of the system with some intuitive graphical user interface.
# The application should consist of the state machine you did in Part 1. The state machine continuously read the temperature of the system as set by the GUI. The read temperature is fed in as input to move the state machine to the next time step, and produce its output.
# The output of the state machine should be displayed in the GUI application. You should be able to see the power of the water pump and DC fan increase when the system's temperature is above the target temperature. Those output powers should change as the temperature change according to your controller.

# Note that the test program in part 2.2 need not be implemented with the real sensor, water pump, and DC fan. It is purely software. We will do the real implementation in Part 3.
'''
2D Group Members:
    > Charlotte Phang
    > Lau Wenkie
    > Mok Jun Neng
    > Martin Tan
    > Dicson Candra
'''

from PIDsm import PID_ControllerSM #import the PID controller state machine

#MAJOR REDO OF GUI

from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.widget import Widget
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.layout import Layout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.slider import Slider
from kivy.uix.progressbar import ProgressBar
import time
import sys


class MainLayout(Screen):
    def __init__(self,**kwargs):
        Screen.__init__(self,**kwargs)
        self.motorController = PID_ControllerSM(30, 10, 0, 1) #initialize the PID controller
        self.fanController = PID_ControllerSM(30, 17, 0, 0.5)
        self.motorController.start()
        self.fanController.start()

    #function called upon when sliders' value in GUI changes
    def motor_output(self):
        #target temperature set in controller is based on value of target temperature slider in GUI
        self.motorController.setTargetTemperature(float(self.ids.targtemp_slider.value)) 
        sys_temp = float(self.ids.systemp_slider.value)
        #system temperature input into controller is based on value of system temperature slider in GUI
        motorOutput = self.motorController.step(sys_temp)
        #displays the percentage output accordingly
        #ids refer to widget with the respective id within kv file
        self.ids.motorout.text = str(round(motorOutput,2))+'%'
        self.ids.motorbar.value = motorOutput
        
    #function called upon when sliders' value in GUI changes  
    def fan_output(self):
        #target temperature set in controller is based on value of slider in GUI
        self.fanController.setTargetTemperature(float(self.ids.targtemp_slider.value))
        sys_temp = float(self.ids.systemp_slider.value)
        #system temperature value determined by slider is used as input into the PID controller SM class
        fanOutput = self.fanController.step(sys_temp)
        #displays the percentage output accordingly
        self.ids.fanout.text = str(round(fanOutput,2))+'%'
        self.ids.fanbar.value = fanOutput
        

class MotorControllerApp(App):
    def build(self):
        return MainLayout()
    
if __name__ == '__main__':
    MotorControllerApp().run()