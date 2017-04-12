from PIDsm import PID_ControllerSM
import matplotlib.pyplot as plt

mass = 40 #grams
specific_heat_cap = 4.18 #J g^-1 K^-1

initialTemp = 35.0
targetTemp = 30
coolantTemp = 25

currTemp = initialTemp
currTime = 0.0

steps = 1000000
simulationTime = 1000 #seconds

offsetPower = 5 #watts

plot = [[currTime], [currTemp]]

dt = float(simulationTime)/steps

controller = PID_ControllerSM(targetTemp,20,0,0)
controller.start()

def Qdot(motorPWM):
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

for i in range(steps):
    currTime = simulationTime*(float(i)/steps)
    net_heat = Qdot(controller.step(float(currTemp))) * dt
    currTemp += net_heat/(specific_heat_cap*mass)
    plot[0].append(currTime)
    plot[1].append(currTemp)

def showPlot(xlist, ylist):
    plt.plot(xlist, ylist, 'r-')
    # plt.axis([0,0,0,0])
    plt.show()

#print plot[1], plot[0]
    
showPlot(plot[0], plot[1])

    