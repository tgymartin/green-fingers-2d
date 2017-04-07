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

class MotorButton(Button):
    def __init__(self,**kwargs):
        Button.__init__(self,**kwargs)
        self.font_size=20
        self.halign='left' 
        self.valign='middle'
        #self.size_hint=(0.2,0.1)

class QuitButton(Button):
    def __init__(self, **kwargs):
        Button.__init__(self,**kwargs)
        self.text='Quit'
        self.font_size=20
        self.pos_hint={'right':1,'bottom':0}
        self.size_hint=(0.2,0.1)

class DefaultLabel(Label):
    def __init__(self, **kwargs):
        super(DefaultLabel, self).__init__(**kwargs)
        self.font_size=20
        self.halign='left' 
        self.valign='middle'

class Empty(Label):
    def __init__(self, **kwargs):
        super(Empty, self).__init__(**kwargs)
        self.text = ''

class ControlPanelScreen(Screen):
    def __init__(self, **kwargs):
        super(ControlPanelScreen, self).__init__(**kwargs) #initialise the properties of the parent class
        self.nRows = 6
        self.layout = GridLayout(cols = 3, rows = self.nRows) #initialise layout
        self.add_widget(self.layout)
        

        #Motor Controls Row
        self.layout.add_widget(DefaultLabel(text = 'Motor Control'))
        self.layout.add_widget(Empty())
        self.layout.add_widget(Empty())
        
        #
        self.layout.add_widget(DefaultLabel(text = 'Motor Control'))
        self.layout.add_widget(DefaultLabel(text = '<display power>'))
        self.layout.add_widget(DefaultLabel(text = '<slider>'))

        # Motor control buttons
        motorPWMButton = MotorButton(text = 'Auto')
        motorStartButton = MotorButton(text = 'Manual')
        motorStopButton = MotorButton(text = 'Stop')
        self.layout.add_widget(motorPWMButton)
        self.layout.add_widget(motorStartButton)
        self.layout.add_widget(motorStopButton)

        self.layout.add_widget(Empty())
        self.layout.add_widget(Empty())
        self.layout.add_widget(Empty())

        #Temperature Control
        self.layout.add_widget(DefaultLabel(text = 'Temperature Settings'))
        self.layout.add_widget(Empty())
        self.layout.add_widget(Empty())

        self.layout.add_widget(DefaultLabel(text = 'Set Temperature'))
        self.layout.add_widget(DefaultLabel(text = '<display set temp>'))
        self.layout.add_widget(DefaultLabel(text = '<set temp slider>'))

        
class TwoDApp(App):
    def build(self):
        sm = ScreenManager(transition=FadeTransition())
        ctrlpanel = ControlPanelScreen(name = 'Control Panel')
        sm.add_widget(ctrlpanel)
        sm.current = 'Control Panel'
        return sm


if __name__== '__main__':
    TwoDApp().run()