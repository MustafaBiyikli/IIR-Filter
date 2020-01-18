# -*- coding: utf-8 -*-
"""
Created on Sun Nov 24 15:23:32 2019

@authors: MUSTAFA & KATARZYNA
"""

class IIR2Filter:
    def __init__(self, sos):
         # FIR Coefficients
        self.b0 = sos[0]; self.b1 = sos[1]; self.b2 = sos[2]
        # IIR Coefficients
        self.a0 = sos[3]; self.a1 = sos[4]; self.a2 = sos[5]
        self.buffer1 = 0
        self.buffer2 = 0
    
    def dofilter(self, x):
        acc_input = x - (self.buffer1*self.a1) - (self.buffer2*self.a2)
        acc_output = (acc_input*self.b0) + (self.buffer1*self.b1) + (self.buffer2*self.b2)
        
        self.buffer2 = self.buffer1
        self.buffer1 = acc_input
        return acc_output

class IIRFilter:
    def __init__(self, sos):
        self.sos = sos
        self.order = len(sos)
        self.slave = []
        for n in range(self.order):
            self.slave.append(IIR2Filter(self.sos[n,:]))
    def dofilter(self, x):
        self.y = x
        for i in range(len(self.sos)):
            self.y = self.slave[i].dofilter(self.y)
        return self.y