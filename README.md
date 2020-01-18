# IIR-Filter
IIR Filter written in Python 3

DirectFormII IIR filter/chain of 2nd order filters, see the Report.pdf file for an in-depth explanation.

See realtime_iir_main.py for an example usage. This uses the Qt library for production the real-time plots. Data acquisiton is performed by an Arduino UNO board. pyfirmata2 library used for setting a constant sampling rate of 100Hz and allowing the Arduino to be programmed in Python.

Arduino best used for mechanical measurements due to limited sampling rate of 100Hz, however, the IIR filter can be used with other data acquisiton boards.

[![Click here for an example usage]](https://www.youtube.com/watch?v=uSm0Zic1wVA)
