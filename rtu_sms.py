#!/usr/bin/env python2
# -*- coding:utf-8 -*-

# RTU SMS 
# 2021/5/24 
import serial
import time

def send_sms(sms_str):
    # Init serial port (115200bps)
    ser = serial.Serial(
        port = '/dev/ttyUSB1',
        baudrate = 115200,
        parity = serial.PARITY_NONE,
        stopbits = serial.STOPBITS_ONE,
        bytesize = serial.EIGHTBITS, 
        timeout = 2
    )

    print (ser.isOpen())
    ser.flushInput()
    ser.flushOutput()

    ## Check Modem
    serial_msg = "AT\r\n"
    ser.write(serial_msg)
    s = ser.readline()
    t = ser.readline()
    print (s, t)
    if (t == "OK\r\n") :
        print ("Modem Normal\r\n")
    else :
        print ("Modem Abnormal\r\n")
        serial_msg = "AT+CFUN=1,1\r\n"
        ser.write(serial_msg)
        print("Wait Reset")
        time.sleep(30)
        ser.flushInput()
        ser.flushOutput()


    serial_cmd = "AT+CSCS=\"IRA\"\r\n"
    print (serial_cmd)
    ser.write(serial_cmd.encode('ascii'))
    print (ser.readline())

    serial_cmd = "AT+CMGF=1\r\n"
    print (serial_cmd)
    ser.write(serial_cmd.encode('ascii'))
    print (ser.readline())

    serial_cmd = "AT+CSMP=,,,0\r\n"
    print (serial_cmd)
    ser.write(serial_cmd.encode('ascii'))
    print (ser.readline())

    #serial_cmd = "AT+CMGS=\"01027416010\"\r\n"
    serial_cmd = "AT+CMGS=\"01027416010\"\r\n"
    print (serial_cmd)
    ser.write(serial_cmd.encode('ascii'))
    time.sleep(1)
    print (ser.readline())

    # Send Message
    serial_msg = "RTU Report\r\n" + sms_str 
    ser.write(serial_msg.encode('ascii'))
    print (ser.readline())
    ser.write(b'\x1a')
    print (ser.readline())

    # Close serial port 
    ser.close()


