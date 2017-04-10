
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
from libdw import sm
from PID import PID


class output_sm(sm.SM):
    def __init__(self):
        self.startState = 0
        self.motorController = PID(-1,0,-1)
        self.kick = 1.0        
        self.kickLambda = 0.01
        self.kickThreshold = 0.01
        self.kickTime = 0.1
        self.currentTime = time.time()
    
    def getNextValues(self,state,inp):
        if state == 0:
#            motor_power = self.motorController(sys_temp)
            if motor_power > 0:
                self.currentTime = time.time()
                state = 1
        if state == 1:
#            controlVal = self.motorController(sys_temp)
            motor_power = self.kick
            self.kick = (1-self.kickLambda)*self.kick + self.kickLambda*controlVal
            if self.kick < (self.kickThreshold + controlVal) or time.time() - self.currentTime > self.kickTime:
                state = 2
            else:
                state = 1
        if state == 2:
            motor_power = self.motorController 

class PD_ControllerSM(sm.SM):
    def __init__(self, targtemp):
        self.startState = 0 
        self.targtemp = targtemp
        self.motorOutput = PID(-1,0,-1)
        
    def getNextValues(self,state,inp):
        if inp > self.targtemp :
            self.motorOutput.setpoint = self.targtemp
            output = self.motorOutput(inp)
            return 1, output
        else:
            return 0,0

class MainLayout(Screen):
  
    def __init__(self,**kwargs):
        Screen.__init__(self,**kwargs)
#        self.motor_output_power = PID(-1,0,0)
#        self.fan_output_power = PID(-1,0,0)
        self.motorController = PD_ControllerSM(self.ids.targtemp_slider.value)
        self.motorController.start()
    
    def motor_output(self):
        sys_temp = float(self.ids.systemp_slider.value)
#        targ_temp = float(self.ids.targtemp_slider.value)
#        self.motor_output_power.setpoint = targ_temp
        motorOutput = self.motorController.step(sys_temp)
        self.ids.motorout.text = str(round(motorOutput*100,2))+'%'
        self.ids.fanout.text = str(round(motorOutput*100,2))+'%'
        self.ids.motorbar.value = motorOutput*100
        
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
    
    
class PID(object): #needs import time
    def __init__(self, Kp = 1, Ki = 0, Kd = 0, min_output = 0, max_output = 1, integrator_min = -sys.maxint, integrator_max = sys.maxint,  derivativeN = 5, backCalc = False, backCalcCoeff = 0.0):
        print 'linwei is a nutter'
        self.Kp = Kp #Proportional constant
        self.Ki = Ki #Integral Constant
        self.Kd = Kd #Derivative Constant

        self.I_val = 0.0
        self.integrator_min = integrator_min
        self.integrator_max = integrator_max
        self.min_output = min_output
        self.max_output = max_output
        self.prevError = 0
        self.prevTime = time.time()-0.001
        self.clamped = False
        
        self.derivIdx = 0
        self.derivN = derivativeN #num of derivatives to average. Increase value to reduce derivative noise. Not too much to reduce derivative dead time.
        self.derivVals = [0 for i in range(derivativeN)]

        #not implemented yet
        self.backCalc = backCalc
        self.backCalcCoeff = backCalcCoeff
        self.prevOut = None
        self.backCalcLevel = 0.0
        self.setpoint = 0.0

    def __call__(self, x):
        #calculate dt = time since previous output measurement
        timeNow = time.time() #get the time once to prevent waiting for execution time
        dt = timeNow - self.prevTime
        self.prevTime = timeNow #save current time as previous time for next reading
        
        #calculate error and P value
        error = self.setpoint - x
        self.P_val = self.Kp * error
        
        # clamp the I value
        if self.clamped == False:
            print 'integrating'
            self.I_val += self.Ki * error * dt

            if self.I_val > self.integrator_max:
                self.I_val = self.integrator_max
            if self.I_val < self.integrator_min:
                self.I_val = self.integrator_min

        # reduce the integral using back calculation if signal is clamped
        if self.backCalc == True and self.clamped == True:
            self.I_val += self.Ki * (error - (self.backCalcCoeff * self.backCalcLevel)) * dt
        
        self.derivVals[self.derivIdx] = (error - self.prevError) / dt
        self.D_val = self.Kd * sum(self.derivVals)/float(self.derivN)
        print error - self.prevError
        self.derivIdx = (self.derivIdx + 1) % self.derivN #advance the index of the list
        self.prevError = error

        output = self.I_val + self.P_val + self.D_val
        self.prevOut = output
        
        #clamp the output signal to the expected output range
        if output > self.max_output:
            self.clamped = True
            output = self.max_output
            self.backCalcLevel = output - self.prevOut
        if output < self.min_output:
            self.clamped = True
            output = self.min_output
            self.backCalcLevel = output - self.prevOut
        else:
            self.clamped = False
        print 'P = %.3f, I = %.6f, D = %.5f, dt = %.3f' %(self.P_val, self.I_val, self.D_val, dt)
        return output

    def set_setpoint(self, setpoint):
        print 'setpoint = %.3f' %(setpoint)
        self.setpoint = setpoint
        

class PD_ControllerSM(sm.SM):
    def __init__(self, targtemp):
        self.startState = 0 
        self.targtemp = targtemp
        self.motorOutput = PID(-1,0,-1)
        
    def getNextValues(self,state,inp):
        if inp > self.targtemp :
            self.motorOutput.setpoint = self.targtemp
            output = self.motorOutput(inp)
            return 1, output
        else:
            return 0,0

class MainLayout(Screen):
  
    def __init__(self,**kwargs):
        Screen.__init__(self,**kwargs)
#        self.motor_output_power = PID(-1,0,0)
#        self.fan_output_power = PID(-1,0,0)
        self.motorController = PD_ControllerSM(self.ids.targtemp_slider.value)
        self.motorController.start()
    
    def motor_output(self):
        sys_temp = float(self.ids.systemp_slider.value)
#        targ_temp = float(self.ids.targtemp_slider.value)
#        self.motor_output_power.setpoint = targ_temp
        motorOutput = self.motorController.step(sys_temp)
        self.ids.motorout.text = str(round(motorOutput*100,2))+'%'
        self.ids.fanout.text = str(round(motorOutput*100,2))+'%'
        self.ids.motorbar.value = motorOutput*100
        
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
    
#        print motorOutput
#        print fanOutput
        
    
#class FloatInput(TextInput):
#
#    pat = re.compile('[^0-9]')
#    def insert_text(self, substring, from_undo=False):
#        pat = self.pat
#        if '.' in self.text:
#            s = re.sub(pat, '', substring)
#        else:
#            s = '.'.join([re.sub(pat, '', s) for s in substring.split('.', 1)])
#        return super(FloatInput, self).insert_text(s, from_undo=from_undo)
    pass
        
class MotorControllerApp(App):
    def build(self):
        return MainLayout()
    
if __name__=='__main__':
    MotorControllerApp().run()