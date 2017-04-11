from PIDsm import PID_ControllerSM #import the PID controller state machine

from kivy.app import App
from kivy.lang import Builder
from kivy.uix.screenmanager import ScreenManager, Screen, FadeTransition
from kivy.uix.widget import Widget
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.layout import Layout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout
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
    
    def motor_output(self):
        self.targTemp = self.ids.targtemp_slider.value
        sys_temp = float(self.ids.systemp_slider.value)
#        targ_temp = float(self.ids.targtemp_slider.value)
#        self.motor_output_power.setpoint = targ_temp
        motorOutput = self.motorController.step(sys_temp)
        self.ids.motorout.text = str(round(motorOutput,2))+'%'
        self.ids.fanout.text = str(round(motorOutput,2))+'%'
        self.ids.motorbar.value = motorOutput
        
    def on_touch_move(self,touch):
        self.motor_output()
        
    def on_touch_up(self,touch):
        self.motor_output()

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