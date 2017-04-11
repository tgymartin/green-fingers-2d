# -*- coding: utf-8 -*-
"""
Created on Mon Apr 10 19:58:35 2017

@author: Mok Jun Neng
"""
import time
import simpy
import math as m
import matplotlib.pyplot as plt
import random

#turn weather on or off
weatherSwitch = True

timeStep = 1


class System:
    def __init__(self,env):
        self.sys_temperature = simpy.Container(env, init=30, capacity=1000)
        #mass of water in g
        self.mass_water = 40
        #heat capacity of water, units is J/g/celcius
        self.C_of_water = 4.18
        
        self.currAmbientTemp = 27.185455348

    def ambientTemperature(self, env):
        while True:
            x = (env.now/3600.0)%24
            self.currAmbientTemp = 0.000058707*x**5 - 0.002951056*x**4 + 0.044551538*x**3 - 0.170349946*x**2 - 0.149160703*x + 27.185455348
        
        
#    def runtime(self,env):
#        while True:
            
        
class SolarPower:
    def __init__(self,env):
        self.solarQin = env.process(self.solar_pOut(env))
        #irradiance units is W/m^2
        self.surface_area = 14.69*10**-4
        
        
    def solar_pOut(self, env):
        
        while True:
            self.time = int(env.now)/3600
            self.irradiance = (-0.000872*self.time**4 + 0.041849*self.time**2  + 6.038294*self.time - 17.125885)*1000
            if self.irradiance <= 0:
                self.irradiance = 0
            temp_change = self.irradiance*self.surface_area/(System.mass_water*System.C_of_water)
            try:
                # print System.sys_temperature.level
                yield System.sys_temperature.put(temp_change)
                yield env.timeout(timeStep)
            except ValueError:
                yield env.timeout(timeStep)
            

class AmbientTemperature:
    def __init__(self, env):
        #units: W/m^2.K
        self.ambientQ = env.process(self.heat_exchange_with_surrounding(env))
        self.heat_transfer_coefficient = 5
        #units: m^2
        self.heat_transfer_area = 14.69*10**-4
        self.temp_ambient = 25

        #Fan Parameters
        self.fanMaxAirSpeed = 0.5 #meters per second
        self.fanMinPWM = 30 #percent

        #Wind
        self.currWindSpeed = 1.0 #meters per second
        self.windVariance = 1.0

    def heat_exchange_with_surrounding(self,env, fanPWM = 100):
        while True:
            self.time = float(env.now)/3600
            #simplified model of ambient temperature in one day
            self.temp_ambient = -2*m.cos(self.time*m.pi/12)+29
            current_temp = System.sys_temperature.level
    #        print 'Temperature due to heat exchange with surrounding: %d'%(current_temp)
            totalWind = self.fanAirSpeed(fanPWM) ################################################################          INPUT FOR FAN PWM, 0 to 100  ###
            if weatherSwitch == True:
                totalWind += self.windSpeed
            heat_exchange = self.convectionCoeff(totalWind) * self.heat_transfer_area * (current_temp - self.temp_ambient)
            temp_change = heat_exchange / (System.mass_water * System.C_of_water)
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

class HeatExchanger:
    def __init__(self, env):
        pass
    
    def heatExchangerQ(self, env, pumpPWM = 100):
        while True:

            if temp_change > 0:
                # print System.sys_temperature.level
                yield System.sys_temperature.get(temp_change)
                yield env.timeout(timeStep)
        
            elif temp_change < 0:
                # print System.sys_temperature.level
                yield System.sys_temperature.put(-temp_change)
                yield env.timeout(timeStep)
        

        
        
#class MotorOutpt:
#    def __initi__(self,env):
#        #units: ml/s
#        self.mass_flow_rate = 0.7
#        
#        
env = simpy.rt.RealtimeEnvironment(factor=0.01, strict = False)
#env = simpy.Environment()
System = System(env)
SolarPower = SolarPower(env)
AmbientTemperature = AmbientTemperature(env)
env.run(until = 3*3600)

plt.plot(c.x, c.y, 'r-')
plt.axis([0,0,0,0])
plt.show()
        
        