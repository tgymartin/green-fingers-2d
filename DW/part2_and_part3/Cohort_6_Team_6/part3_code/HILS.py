import time
import simpy
import math as m
import matplotlib.pyplot as plt
import random
import zmq

#turn weather on or off
weatherSwitch = True

timeStep = 1

ambientTempPlot = [list(), list()]
solarPlot = [list(), list()]
containerPlot = [list(), list()]

#Class that initializes a container as shared resources in the environment 
#Shared resource is temperature which relates to the energy of the system
#The processe which always increase the temperature of the system is solar radiation, while the processes which can either increase or decrease the temperature of the
#system are heat convection through air and heat exchange through the heat exchanger
class System:
    def __init__(self,env):
        self.sys_temperature = simpy.Container(env, init=30, capacity=1000)
        self.mass_water = 40 #grams
        self.C_of_water = 4.18 #J g^-1 K^-1
        self.mc = self.mass_water * self.C_of_water
        self.targetTemperature = 30

#Modelled ambient temperature throughout a day
class AmbientTemperature:
    def __init__(self, env):
        self.currAmbientTemp = 26.035699489
        self.temp = env.process(self.ambientTemperature(env))

    def ambientTemperature(self, env):
        while True:
            time = env.now/3600.0
            x = time%24
            self.currAmbientTemp = -0.000002986*x**6 + 0.000251496*x**5 - 0.007575376*x**4 + 0.094543418*x**3 - 0.404532576*x**2 + 0.303541658*x + 26.035699489 #Taken from accuweather.com, plotted in day_temp.xlsx
            ambientTempPlot[1].append(self.currAmbientTemp)
            ambientTempPlot[0].append(env.now)
            containerPlot[1].append(System.sys_temperature.level)
            containerPlot[0].append(env.now)
            yield env.timeout(timeStep)
        
#Process of solar power input
class SolarPower:
    def __init__(self,env):
        self.solarQin = env.process(self.solar_pOut(env))
        #irradiance units is W/m^2
        self.surface_area = 10*10**-4
        self.emmisivity = 0.3
    
    #solar power input into the system is modelled using online data, taking into account of day-night cycle
    def solar_pOut(self, env):
        
        while True:
            self.time = (float(env.now)/3600) % 24
            self.irradiance = self.emmisivity*(-0.000872*self.time**4 + 0.041849*self.time**3 - 0.753783*self.time**2  + 6.038294*self.time - 17.125885)*1000.0
            if self.irradiance <= 0:
                self.irradiance = 0
            solarPlot[0].append(env.now)
            solarPlot[1].append(self.irradiance)
            temp_change = self.irradiance*self.surface_area/(System.mass_water*System.C_of_water)

            try:
                # print System.sys_temperature.level
                yield System.sys_temperature.put(temp_change)
                yield env.timeout(timeStep)
            except ValueError:
                yield env.timeout(timeStep)
            
#Heat convection process in which the heat transfer can be affected by factors such as natural wind speed and speed of the DC fan
class Convection:
    def __init__(self, env):
        #units: W/m^2.K
        self.ambientQ = env.process(self.heat_exchange_with_surrounding(env))
        self.heat_transfer_coefficient = 5
        #units: m^2
        self.heat_transfer_area = 146.9*10**-4
        self.temp_ambient = 25

        #Fan Parameters
        self.fanMaxAirSpeed = 0.5 #meters per second
        self.fanMinPWM = 30 #percent

        #Wind
        self.currWindSpeed = 1.0 #meters per second
        self.windVariance = 1.0


    def heat_exchange_with_surrounding(self, env):
        while True:
            self.time = float(env.now)/3600
            #simplified model of ambient temperature in one day
            self.temp_ambient = AmbientTemperature.currAmbientTemp
            current_temp = System.sys_temperature.level
    #        print 'Temperature due to heat exchange with surrounding: %d'%(current_temp)
            totalWind = self.fanAirSpeed(100) ################################################################          INPUT FOR FAN PWM, 0 to 100  ###
#            if weatherSwitch == True:
#                totalWind += self.windSpeed(self.time)
            heat_exchange = self.convectionCoeff(totalWind) * self.heat_transfer_area * (current_temp - self.temp_ambient)
            temp_change = heat_exchange / System.mc
            if temp_change > 0:
                # print System.sys_temperature.level
                yield System.sys_temperature.get(temp_change)
                yield env.timeout(timeStep)
        
            elif temp_change < 0:
                # print System.sys_temperature.level
                yield System.sys_temperature.put(-temp_change)
                yield env.timeout(timeStep)

    def windSpeed(self, timeofday): #source: http://www.wind-power-program.com/wind_statistics.htm
        self.currWindSpeed += (random.random() - 0.5) * 2 * self.windVariance * random.weibullvariate(1, 0.5 + random.random())
        if self.currWindSpeed < 0:
            self.currWindSpeed = 0
        return self.currWindSpeed
    
    def fanAirSpeed(self, fanPWM):
        if fanPWM > self.fanMinPWM:
            airSpeed = self.fanMaxAirSpeed * (fanPWM - self.fanMinPWM)/(100.0 - self.fanMinPWM)
        else:
            airSpeed = 0.0
        return airSpeed
    
    def convectionCoeff(self, totalAirSpeed): #source: http://www.engineeringtoolbox.com/convective-heat-transfer-d_430.html
        coeff = 10.45 - totalAirSpeed + 10 * (totalAirSpeed)**0.5
        return coeff

#Heat exchanger process which is controlled by a PID state machine controller
class HeatExchanger:
    def __init__(self, env):
        self.HeatExchanger = env.process(self.heatExchangerQ(env))
        self.pumpSupplyVoltage = 6.0
        self.waterTemp = 27.0
#        self.motorController = PID_ControllerSM(System.targetTemperature, 5, 0, 0)
#        self.motorController.start()
        self.context = zmq.Context()
        #  Socket to talk to server
        self.socket = self.context.socket(zmq.REQ)
        self.socket.connect("tcp://localhost:5555")
    
    def heatExchangerQ(self, env):
        while True:
            self.sendCurrTemp()
            motorPWM = self.getControllerPWM()
            pumpVoltage = self.pumpSupplyVoltage * motorPWM / 100.0
            if pumpVoltage < 6:
                pumpVoltage = 6
            if pumpVoltage < 2.5:
                pumpVoltage = 2.5
            if motorPWM != 0:    
                conductance = 0.014318934*pumpVoltage**3 - 0.240144362*pumpVoltage**2 + 1.341548910*pumpVoltage - 1.3523 #empirical data (see excel)
            else:
                conductance = 0.01
            deltaT = System.sys_temperature.level - self.waterTemp
            
            temp_change = deltaT * conductance / System.mc
            if temp_change > 0:
                # print System.sys_temperature.level
                yield System.sys_temperature.get(temp_change)
                yield env.timeout(timeStep)
        
            elif temp_change < 0:
                # print System.sys_temperature.level
                yield System.sys_temperature.put(-temp_change)
                yield env.timeout(timeStep)
    
    #sendCurrTemp and getControllerPWM are functions that communicate values with the PID controller through a server
    def sendCurrTemp(self):
        self.socket.send(b'%s'%(str(System.sys_temperature.level)))
#        print "Sent temperature:   " + str(System.sys_temperature.level)
        
    def getControllerPWM(self):
        message = self.socket.recv()
#        print "Received PWM:   " + message
        return float(message)
            
            
if __name__ == '__main__':
    try:
        env = simpy.rt.RealtimeEnvironment(factor=0.00001, strict = False)
        #env = simpy.Environment()
        System = System(env)
        SolarPower = SolarPower(env)
        AmbientTemperature = AmbientTemperature(env)
        Convection = Convection(env)
        HeatExchanger = HeatExchanger(env)
        env.run(until = 7*24*3600)
        
#        def showPlot(xlist, ylist):
#            plt.plot(xlist, ylist, 'r-')
#            # plt.axis([0,0,0,0])
#            plt.show()
#        
#        showPlot(ambientTempPlot[0], ambientTempPlot[1])
#        showPlot(solarPlot[0], solarPlot[1])
#        showPlot(containerPlot[0], containerPlot[1])
    except KeyboardInterrupt:
        exit()
        