from libdw import sm
import time
import os
import zmq

class PID_ControllerSM(sm.SM):
    def __init__(self, targTemp, Kp, Ki, Kd):
        self.startState = (0, [0, time.time(), 0], 0) 
        self.targTemp = targTemp

        self.Kp = Kp #Proportional constant
        self.Ki = Ki #Integral Constant
        self.Kd = Kd #Derivative Constant
        
        self.pumpMinPWM = 35.0 #percent

        self.Imax = 10
        self.Imin = -10

        self.kickTime = 0.1 #seconds
    
    def setTargetTemperature(self,temperature):
        self.targTemp = temperature
        
        
    def getNextValues(self, state, inp):
        
        PIDlist = self.PID(state[1], inp) #PIDlist is (outputPWM, [error, currTime, Ival, 0])
        if state[0] == 0: #off state
            if PIDlist[0] <= self.pumpMinPWM:
                nextState = 0
#                socket.send(b"0")
                return (nextState, PIDlist[1], 0), 0
            else:
                nextState = 1 #kickstart the motor
#                socket.send(b"100")
                return (nextState, PIDlist[1], time.time()), 100

        if state[0] == 1: #kickstart motor to prevent stalling at low voltages
            if time.time() - state[2] > self.kickTime: #kickstart for a limited time
                nextState = 2
#                socket.send(b"PIDlist[0]")
                return (nextState, PIDlist[1], 0), PIDlist[0] 
            else:
                nextState = 1
#                socket.send(b"100")
                return (nextState, PIDlist[1], state[2]), 100
            
        if state[0] == 2: #PID control
            if PIDlist[0] > self.pumpMinPWM:
                nextState = 2
#                socket.send(b"PIDlist[0]")
                return (nextState, PIDlist[1], 0), PIDlist[0]
            else:
                nextState = 0
#                socket.send(b"0")
                return (nextState, PIDlist[1], 0), 0

    def PID(self, state, inp): #function to calculate the next PID value used in getNextValues
        error = inp - self.targTemp
        prevError = state[0] #get the previous error from the state
        currTime = time.clock() #get current time in seconds
        dt = currTime - state[1] #find the (current time) - (previous time)
        if dt == 0: #prevent divide by 0 error
            dt = 0.00001
        
        #NOT USED: calculate I value and clamp if too large.
        Ival = state[2] + (self.Ki * error* dt)
        if Ival > self.Imax:
            Ival = self.Imax
        if Ival < self.Imin:
            Ival = self.Imin
        
        outputPWM = self.pumpMinPWM + (self.Kp * error) + Ival + (self.Kd * (error - prevError) / dt)
        #clamp the PWM to be within 0 to 100
        if outputPWM > 100:
            outputPWM = 100
        if outputPWM < self.pumpMinPWM: #pump has a stall point at roughly 2 volts.
            outputPWM = self.pumpMinPWM
        
        return (outputPWM, [error, currTime, Ival]) #return the PID value, and pass the error, current time and Ival to the next 'getNextValues' function.


#Code below for interfacing with the Hardware in Loop Simulation
if __name__ == '__main__':
    p = PID_ControllerSM(30,20,0,1) #create a controller object with target 30 deg C
    p.start()
    context = zmq.Context()
    socket = context.socket(zmq.REP)
    socket.bind("tcp://*:5555")
    try:
        while True:
            message = socket.recv() #wait for a temperature
            print("Received request: %s" % message)
            socket.send(b'%s' %(str(p.step(float(message))))) #return a PWM value to the Hardware in Loop Simulation
    except KeyboardInterrupt: #exit when user presses Ctrl-C
        del socket
        exit()