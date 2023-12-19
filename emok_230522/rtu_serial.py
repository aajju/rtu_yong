#!/usr/bin/env python2
# -*- coding: utf-8 -*-

import serial
import time

SERIALPORT1 = "/dev/ttyUSB0"
SERIALPORT2 = "/dev/ttyUSB1"
SERIALPORT3 = "/dev/ttyUSB2"

BAUDRATE = 38400

ser1 = serial.Serial(SERIALPORT1, BAUDRATE)
ser1.bytesize = serial.EIGHTBITS
ser1.parity = serial.PARITY_NONE
ser1.stopbit = serial.STOPBITS_ONE
ser1.timeout = 2
ser1.xonxoff = False
ser1.rtscts = False
ser1.dsrdtr = False
ser1.writeTimeout = 0

try:
    ser1.open()
except Exception as e:
    print ("Exception: Opening serial port : " + str(e))

if ser1.isOpen():
    try:
        ser1.flushInput()
        ser1.flushOutput()
        count = 1
        while True:
            ser1.write("01,01\r\n".encode('ascii'))
            ret = ser1.readline().decode('ascii')
            print ret
            ch_num = ret.split(',')[0]
            det_num = ret.split(',')[1]
            lc_hz = ret.split(',')[2]
            volt = ret.split(',')[3]

            print ch_num
            print det_num
            print lc_hz
            print volt
            
            time.sleep(0.5)
        
            ser1.write("01,02\r\n".encode('ascii'))
            ret = ser1.readline().decode('ascii')
            print ret
            time.sleep(0.5)

            print count

            count = count + 1
            if (count > 100):
                break
    except Exception as e:
        print ("Error communicating...: " + str(e))
else:
    print ("Cannot open serial port.")


