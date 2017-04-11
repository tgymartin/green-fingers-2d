# -*- coding: utf-8 -*-
"""
Created on Mon Apr 10 19:58:35 2017

@author: Mok Jun Neng
"""
import time
import simpy
import math as m
import matplotlib.pyplot as plt


class System:
    def __init__(self,env):
        self.sys_temperature = simpy.Container(env, init=30, capacity=1000)
        #mass of water in g
        self.mass_water = 40
        #heat capacity of water, units is J/g/celcius
        self.C_of_water = 4.18
        
#    def runtime(self,env):
#        while True:
            
        
class SolarPower:
    def __init__(self,env):
        self.solarQin = env.process(self.solar_pOut(env))
        #irradiance units is W/m^2
        self.surface_area = 14.69*10**-4
        
        
    def solar_pOut(self,env):
        
        while True:
            self.time = int(env.now)/3600
            self.irradiance = (-0.000872*self.time**4 + 0.041849*self.time**2  + 6.038294*self.time - 17.125885)*1000
            temp_change = self.irradiance*self.surface_area/(System.mass_water*System.C_of_water)
            try:
                print System.sys_temperature.level  
                yield System.sys_temperature.put(temp_change)
                yield env.timeout(1)
            except ValueError:
                yield env.timeout(1)
            
        

class AmbientTemperature:
    def __init__(self,env):
        #units: W/m^2.K
        self.ambientQ = env.process(self.heat_exchange_with_surrounding(env))
        self.heat_transfer_coefficient = 5
        #units: m^2
        self.heat_transfer_area = 14.69*10**-4
        self.temp_ambient = 25
#        -2*m.cos(t*m.pi/12)+29
        
    
    def heat_exchange_with_surrounding(self,env):
        while True:
            self.time = int(env.now)/3600
            #simplified model of ambient temperature in one day
            self.temp_ambient = -2*m.cos(self.time*m.pi/12)+29
            current_temp = System.sys_temperature.level
    #        print 'Temperature due to heat exchange with surrounding: %d'%(current_temp)
            heat_exchange = self.heat_transfer_coefficient*self.heat_transfer_area*(current_temp - self.temp_ambient)
            temp_change = heat_exchange/(System.mass_water*System.C_of_water)
            if temp_change > 0:
                print System.sys_temperature.level
                yield System.sys_temperature.get(temp_change)
                yield env.timeout(1)
        
            else:
                temp_change = abs(temp_change)
                print System.sys_temperature.level
                yield System.sys_temperature.put(temp_change)
                yield env.timeout(1)
        
        
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
env.run()

plt.plot(c.x, c.y, 'r-')
plt.axis([0,0,0,0])
plt.show()
        
        