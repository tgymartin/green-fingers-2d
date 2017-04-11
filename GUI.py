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

from PIDsm import PID_ControllerSM #import the PID controller state machine

#MAJOR REDO OF GUI

from kivy.app import App
from kivy.lang import Builder
from kivy.uix.screenmanager import ScreenManager, Screen, FadeTransition
from kivy.uix.widget import Widget
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.layout import Layout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.textinput import TextInput
from kivy.uix.slider import Slider
from kivy.uix.progressbar import ProgressBar
from kivy.uix.textinput import TextInput
import time
import sys


class MainLayout(Screen):
    def __init__(self,**kwargs):
        Screen.__init__(self,**kwargs)
    #    self.motor_output_power = PID_ControllerSM(-1,0,0)
    #    self.fan_output_power = PID_ControllerSM(-1,0,0)
        
        self.motorController = PID_ControllerSM(30,10,0,0)
        self.motorController.start()
    
    def updateScreen(self):
        pass



    def motor_output(self):
        PID_ControllerSM.targTemp = float(self.ids.targtemp_slider.value)
        sys_temp = float(self.ids.systemp_slider.value)
#        targ_temp = float(self.ids.targtemp_slider.value)
#        self.motor_output_power.setpoint = targ_temp
        motorOutput = self.motorController.step(sys_temp)
        self.ids.motorout.text = str(round(motorOutput,2))+'%'
        self.ids.fanout.text = str(round(motorOutput,2))+'%'
        self.ids.motorbar.value = motorOutput
        
    # def on_touch_move(self,touch):
    #     self.motor_output()
        
    # def on_touch_up(self,touch):
    #     self.motor_output()

    def motorandfan_output(self):
#        print float(self.ids.systemp.text)
#        print float(self.ids.targtemp.text)
        sys_temp = float(self.ids.systemp_slider.value)
        targ_temp = float(self.ids.targtemp_slider.value)
        self.motor_output_power.setpoint = targ_temp
        self.fan_output_power.setpoint = targ_temp
        motorOutput = self.motor_output_power(sys_temp)
        self.ids.motorout.text = str(round(motorOutput,3))
    
        fanOutput = self.fan_output_power(sys_temp)
        self.ids.fanout.text = str(round(fanOutput,3))

class MotorControllerApp(App):
    def build(self):
        return MainLayout()
    
if __name__ == '__main__':
    MotorControllerApp().run()