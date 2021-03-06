import time
import sys

class PID(object): #needs import time
    def __init__(self, Kp = 1, Ki = 0, Kd = 0, min_output = 0, max_output = 1, integrator_min = -sys.maxint, integrator_max = sys.maxint,  derivativeN = 1, backCalc = False, backCalcCoeff = 0.0):
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
        if dt == 0:
            dt = 0.0001 #do not allow division by zero
        self.prevTime = timeNow #save current time as previous time for next reading
        
        #calculate error and P value
        error = self.setpoint - x
        self.P_val = self.Kp * error
        
        # clamp the I value
        if self.clamped == False:
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