# -*- coding: utf-8 -*-
"""
Created on Fri Apr 07 17:00:48 2017

@author: Mok Jun Neng
"""

import time

#kivy dependencies
from kivy.app import App
from kivy.lang import Builder
from kivy.uix.screenmanager import ScreenManager, Screen, FadeTransition
from kivy.uix.widget import Widget
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.gridlayout import GridLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.textinput import TextInput
from kivy.clock import Clock
from kivy.uix.slider import Slider



class ControlPanelScreen(Screen):
    def __init__(self, **kwargs):
        super(ControlPanelScreen, self).__init__(**kwargs) #initialise the properties of the parent class
#    def auto_mode(self,instance):
#    def manual_mode(self,instance):
#        
#    def stop_motor(self,instance):
        
        pass
        
class TwoDApp(App):
    def build(self):
        sm = ScreenManager(transition=FadeTransition())
        ctrlpanel = ControlPanelScreen(name = 'Control Panel')
        sm.add_widget(ctrlpanel)
        sm.current = 'Control Panel'
        return sm


if __name__== '__main__':
    TwoDApp().run()