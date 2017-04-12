# SIMULATOR FOR CALCULATING K VALUES

# Our group chose to implement a PD controller as the derivative term is used to add a phase lead, thus 'predicting' the error. 
# This causes the controller to reduce its output if it is approaching the target too quickly, preventing overshooting the target.
# Preventing of overshoot is crucial in a heat exchanger system that we are implementing as there is no possibility of adding heat back
# into the algae flask once it is removed. i.e. no overshoot can be tolerated.

# However, a large derivative gain will cause the controller to act as if it is 'overdamped' and thus will reach the target temperature
# very slowly. Using this file, we are able to tune the Kp (proportional gain) and Kd (derivative gain).

# You may have noticed we implemented a PID controller in the PIDsm module as we were initially considering adding the integral term
# However, we have set the integral gain to zero, thus it can be considered to be a PD controller.

from PIDsm import PID_ControllerSM
import matplotlib.pyplot as plt

mass = 40 #grams
specific_heat_cap = 4.18 #J g^-1 K^-1

initialTemp = 35.0 #deg C
targetTemp = 30 #deg C
coolantTemp = 25 #deg C

currTemp = initialTemp
currTime = 0.0 #seconds

steps = 1000000 #number of steps (Euler Method Numerical Integration)
simulationTime = 1000 #seconds

offsetPower = 5 #watts (assume constant heat input from sun, etc.)

plot = [[currTime], [currTemp]] #List of list to save coordinates for graphing

dt = float(simulationTime)/steps #subdividing simulation time into discrete time steps

controller = PID_ControllerSM(targetTemp,20,0,1) #create the controller state machine
controller.start() #start the state machine

def Qdot(motorPWM): #function to calculate heat rate
    if motorPWM != 0:
        pumpVoltage = 6.0 * motorPWM
        if pumpVoltage > 6.0:
            pumpVoltage = 6.0
        if pumpVoltage < 2.5:
            pumpVoltage = 2.5
        conductance = 0.014318934*pumpVoltage**3 - 0.240144362*pumpVoltage**2 + 1.341548910*pumpVoltage - 1.3523 #empirical data (see excel)
    else:
        conductance = 0.01
    return offsetPower + (coolantTemp- currTemp) * conductance

for i in range(steps): #numerical integration
    currTime = simulationTime*(float(i)/steps)
    net_heat = Qdot(controller.step(float(currTemp))) * dt #small amount of heat added/removed from the system
    currTemp += net_heat/(specific_heat_cap*mass) #small change in temperature due to the small amount of heat added/removed
    plot[0].append(currTime) #append to list for plotting
    plot[1].append(currTemp) #append to list for plotting

def showPlot(xlist, ylist): #function to show plot
    plt.plot(xlist, ylist, 'r-')
    # plt.axis([0,0,0,0])
    plt.show()

#print plot[1], plot[0]
    
showPlot(plot[0], plot[1]) #show plot