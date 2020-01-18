# -*- coding: utf-8 -*-
"""
Created on Fri Nov 22 16:45:29 2019

@authors: MUSTAFA & KATARZYNA
"""

#!/usr/bin/python3

import sys

import pyqtgraph as pg
from pyqtgraph.Qt import QtCore, QtGui

import numpy as np; import scipy.signal as signal
from pyfirmata2 import Arduino

import IIR2Filter as iir

PORT = Arduino.AUTODETECT   # Windows
# PORT = '/dev/ttyUSB0'     # Linux

# LED pins
yellow_LED = 5; red_LED = 6

# Avtivation Threshold [V] - for filtered signal
THRESHOLD = 0.035

# create a global QT application object
app = QtGui.QApplication(sys.argv)

# signals to all threads in endless loops
running = True
pg.setConfigOption('background', 'k')
pg.setConfigOption('foreground', 'w')

class AddPlot:
    '''
    Feed the class with:
        linecolor - i.e: 'k', 'w', 'b', 'r', 'g', 'y'\n
        title - i.e: 'AmazingPlot'\n
        xlabel & ylabel in string format\n
        position in list format - i.e: [2, 1] for 2nd row 1st column\n
        yrange & xrange in list format\n
    '''
    win = pg.GraphicsWindow()
    win.setWindowTitle("IIR Filter")

    def __init__(self, linecolor, title, xlabel, ylabel, position, yrange, xrange=[0,600]):
        self.plt = self.win.addPlot(*position)
        self.plt.setTitle(title)
        self.plt.setLabel('bottom', xlabel); self.plt.setLabel('left', ylabel)
        self.plt.setFixedWidth(self.win.width()/2.1); self.plt.setFixedHeight(self.win.height()/2.1)
        self.plt.setYRange(*yrange); self.plt.setXRange(*xrange)
        self.curve = self.plt.plot(pen=pg.mkPen(linecolor, width=2))
        self.data = []
        self.datalength = xrange[1] - xrange[0]
        self.red_LED_timer = []; self.yellow_LED_timer = []
        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.update)
        self.timer.start(100)
        self.win.show()
            
    def update(self):
        self.data=self.data[-self.datalength:]
        self.plt.setFixedWidth(self.win.width()/2.1); self.plt.setFixedHeight(self.win.height()/2.1)
        if self.data:
            self.curve.setData(np.hstack(self.data))
        
        if board.digital[red_LED].read() == 1:
            self.red_LED_timer.append(self.data)
            if len(self.red_LED_timer) == 30:
                board.digital[red_LED].write(0)
        elif board.digital[red_LED].read() == 0:
            self.red_LED_timer.clear()

        if board.digital[yellow_LED].read() == 1:
            self.yellow_LED_timer.append(self.data)
            if len(self.yellow_LED_timer) == 30:
                board.digital[yellow_LED].write(0)
        elif board.digital[yellow_LED].read() == 0:
            self.yellow_LED_timer.clear()            

    def addData(self,d):
        self.data.append(d)

# Let's create two instances of plot windows
Plot1 = AddPlot('y', 'X-Axis [raw]', 'Samples', 'Signal [V]', [1, 1], [0.4, 0.6])
Plot2 = AddPlot('r', 'Y-Axis [raw]', 'Samples', 'Signal [V]', [2, 1], [0.4, 0.6])
Plot3 = AddPlot('y', 'X-Axis [filtered]', 'Samples', 'Signal [V]', [1, 2], [-0.06, 0.06])
Plot4 = AddPlot('r', 'Y-Axis [filtered]', 'Samples', 'Signal [V]', [2, 2], [-0.06, 0.06])

# sampling rate: 100Hz
Fs = 100
# Cut off frequency [Hz]
cut_off = 20

# Creation of the coeffs for high-pass
f1 = cut_off/Fs * 2
sos = signal.butter(6, [f1], 'high', output='sos')

# Feed the sos coefficients into the FIR filter for each axis
IIR_X = iir.IIRFilter(sos)
IIR_Y = iir.IIRFilter(sos)

# called for every new sample which has arrived from the Arduino
def callBack(data):
    # send the sample to the plotwindow
    ch0 = data
    ch0_filtered = abs(IIR_X.dofilter(ch0))
    Plot1.addData(ch0)
    Plot3.addData(ch0_filtered)
    if ch0_filtered > THRESHOLD:
        board.digital[yellow_LED].write(1)
    
    ch1 = board.analog[1].read()
    if ch1:
        Plot2.addData(ch1)
        ch1_filtered = abs(IIR_Y.dofilter(ch1))
        Plot4.addData(ch1_filtered)
        if ch1_filtered > THRESHOLD:
            board.digital[red_LED].write(1)

# Get the Ardunio board.
board = Arduino(PORT)

# Set the sampling rate in the Arduino
board.samplingOn(1000 / Fs)

# Register the callback which adds the data to the animated plot
board.analog[0].register_callback(callBack)
    
# Enable the callback
board.analog[0].enable_reporting()
board.analog[1].enable_reporting()

# showing all the windows
app.exec_()

# needs to be called to close the serial port
board.exit()

print("Finished")