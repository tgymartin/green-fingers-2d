from libdw import sm

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
    
#state [0] is state num 0 = off, 1 = kick, 2 = on
#state1
    #0 is prev err, 
    #1 is prev time
    #2 is I value
#state 3 is kick start time

#output
# 0 is pump PWM from 1 to 100
# 1 is fan pwm from 1 to 100

    def getNextValues(self, state, inp):
        PIDlist = self.PID(state[1], inp) #PIDlist is (outputPWM, [error, currTime, Ival, 0])
        if state[0] == 0: #off state
            if PIDlist[0] <= self.pumpMinPWM:
                nextState = 0
                return (nextState, PIDlist[1], 0), 0
            else:
                nextState = 1 #kickstart the motor
                return (nextState, PIDlist[1], time.time()), 100

        if state[0] == 1: #kickstart motor to prevent stalling at low voltages
            if time.time() - state[2] > self.kickTime: #kickstart for a limited time
                nextState = 2
                return (nextState, PIDlist[1], 0), PIDlist[0] 
            else:
                nextState = 1
                return (nextState, PIDlist[1], state[2]), 100
            
        if state[0] == 2: #PID control
            if PIDlist[0] > self.pumpMinPWM:
                nextState = 2
                return (nextState, PIDlist[1], 0), PIDlist[0]
            else:
                nextState = 0
                return (nextState, PIDlist[1], 0), 0

    def PID(self, state, inp): #function to calculate the next PID value used in getNextValues
        error = inp - self.targTemp
        prevError = state[0]
        currTime = time.time()
        dt = currTime - state[1]
        if dt == 0: #prevent divide by 0 error
            dt = 0.0001
        
        #calculate I value and clamp if too large
        Ival = state[2] + (self.Ki * error* dt)
        if Ival > self.Imax:
            Ival = self.Imax
        if Ival < self.Imin:
            Ival = self.Imin
        
        outputPWM = self.pumpMinPWM + (self.Kp * error) + Ival + (self.Kd * (error - prevError) / dt)
        #clamp the PWM to be within 0 to 100
        if outputPWM > 100:
            outputPWM = 100
        if outputPWM < self.pumpMinPWM:
            outputPWM = self.pumpMinPWM
        
        return (outputPWM, [error, currTime, Ival]) #return the PID value