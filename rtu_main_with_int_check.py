#!/usr/bin/env python2
# -*- coding:utf-8 -*-

import requests
import serial
import time

# Detector Value
siteId_string = "GUMDAN01"
#siteId_string = "bioptech01"
status_string = "1"
TimeInterval = 10 # 60 x 5sec(0.1sec x 5 det x 10 times(MAX_DOUBLE_CHECK))  x 2ch(com3,com4) = 600sec = 10min
#TimeInterval = 60 # 60 x 5sec(0.1sec x 5 det x 10 times(MAX_DOUBLE_CHECK))  x 2ch(com3,com4) = 600sec = 10min
#TimeInterval = 10  # 30 min for LC

# Waiting count_times for valid status
MAX_DOUBLE_CHECK = 10 
#MAX_DOUBLE_CHECK = 180  # for 3 min waiting for LC  

#url = 'http://192.168.100.22:8080/Api/Sensor/getTest'
url = 'http://192.168.0.5:8080/Api/Sensor/getTest'
#url2 = 'http://192.168.0.6:8080/Api/Sensor/getTest'
url2 = 'https://api.undercitysolution.com/Api/Sensor/getTest'
url_error = 'http://192.168.100.1:8080/Api/Sensor/getTest'
headers = {'Content-Type' : 'application/x-www-form-urlencoded'}

# XML Text Header & Tail
xml_text_header = "xmlText=<XML>"
xml_text_tail = "</XML>"
xml_det_header = "<detector>"
xml_det_tail = "</detector>"

#LC Tlanslation
ref_hz = (105920, 75410, 62080, 54850, 50280, 46840, 44380, 42440, 40930, 39610, 38480, 37530, 36720, 36000, 35300, 35040)

SERIALPORT = ("/dev/ttyUSB0", "/dev/ttyUSB1", "/dev/ttyUSB2")   #tuple
g_serial_port = ["ser1","ser2","ser3"]                          #list

#CH x DET XML TEXT
g_xml_text = [  ["ch1_det1", "ch1_det2", "ch1_det3", "ch1_det4", "ch1_det5"], 
                ["ch2_det1", "ch2_det2", "ch2_det3", "ch2_det4", "ch2_det5"], 
                ["ch3_det1", "ch3_det2", "ch3_det3", "ch3_det4", "ch3_det5"], 
                ["ch4_det1", "ch4_det2", "ch4_det3", "ch4_det4", "ch4_det5"], 
                ["ch5_det1", "ch5_det2", "ch5_det3", "ch5_det4", "ch5_det5"], 
                ["ch6_det1", "ch6_det2", "ch6_det3", "ch6_det4", "ch6_det5"]] 

#CH x DET Distance Data
g_distance_val = [  ["ch1_det1", "ch1_det2", "ch1_det3", "ch1_det4", "ch1_det5"], 
                    ["ch2_det1", "ch2_det2", "ch2_det3", "ch2_det4", "ch2_det5"], 
                    ["ch3_det1", "ch3_det2", "ch3_det3", "ch3_det4", "ch3_det5"], 
                    ["ch4_det1", "ch4_det2", "ch4_det3", "ch4_det4", "ch4_det5"], 
                    ["ch5_det1", "ch5_det2", "ch5_det3", "ch5_det4", "ch5_det5"], 
                    ["ch6_det1", "ch6_det2", "ch6_det3", "ch6_det4", "ch6_det5"]] 

#CH x DET Volt Data
g_volt_val = [  ["ch1_det1", "ch1_det2", "ch1_det3", "ch1_det4", "ch1_det5"], 
                ["ch2_det1", "ch2_det2", "ch2_det3", "ch2_det4", "ch2_det5"], 
                ["ch3_det1", "ch3_det2", "ch3_det3", "ch3_det4", "ch3_det5"], 
                ["ch4_det1", "ch4_det2", "ch4_det3", "ch4_det4", "ch4_det5"], 
                ["ch5_det1", "ch5_det2", "ch5_det3", "ch5_det4", "ch5_det5"], 
                ["ch6_det1", "ch6_det2", "ch6_det3", "ch6_det4", "ch6_det5"]] 

#CH x DET Status Data
g_status_val = [["2", "2", "2", "2", "2"], 
                ["2", "2", "2", "2", "2"], 
                ["2", "2", "2", "2", "2"], 
                ["2", "2", "2", "2", "2"], 
                ["2", "2", "2", "2", "2"], 
                ["2", "2", "2", "2", "2"]] 

#CH x DET Status Data Saved
g_status_saved_val = [  ["2", "2", "2", "2", "2"], 
                        ["2", "2", "2", "2", "2"], 
                        ["2", "2", "2", "2", "2"], 
                        ["2", "2", "2", "2", "2"], 
                        ["2", "2", "2", "2", "2"], 
                        ["2", "2", "2", "2", "2"]] 



#Hz to Distance Translation
def get_distance(lc_hz):
    #determine distance table
    if lc_hz > ref_hz[0]:
        distance = 5
    elif lc_hz > ref_hz[1]:
        distance = 65
    elif lc_hz > ref_hz[2]:
        distance = 125
    elif lc_hz > ref_hz[3]:
        distance = 185
    elif lc_hz > ref_hz[4]:
        distance = 240
    elif lc_hz > ref_hz[5]:
        distance = 300
    elif lc_hz > ref_hz[6]:
        distance = 360
    elif lc_hz > ref_hz[7]:
        distance = 420
    elif lc_hz > ref_hz[8]:
        distance = 480
    elif lc_hz > ref_hz[9]:
        distance = 540
    elif lc_hz > ref_hz[10]:
        distance = 600
    elif lc_hz > ref_hz[11]:
        distance = 660
    elif lc_hz > ref_hz[12]:
        distance = 720
    elif lc_hz > ref_hz[13]:
        distance = 780
    elif lc_hz > ref_hz[14]:
        distance = 840
    elif lc_hz > ref_hz[15]:
        distance = 870
    else:
        distance = 1000


    return distance


#XML Text Out
def make_xml_text(ch_num, det_num, distance, volt, status):
    global siteId_string, status_string
    global g_xml_text

    xml_text_siteId = "<siteId>" + siteId_string + "</siteId>"
    xml_text_chNum = "<chNum>" + ch_num + "</chNum>"
    xml_text_detNum = "<detNum>" + det_num + "</detNum>"
    #xml_text_status = "<status>" + status_string + "</status>"
    xml_text_status = "<status>" + status + "</status>"
    xml_text_distance = "<distance>" + distance + "</distance>"
    xml_text_btAmt = "<btAmt>" + volt + "</btAmt>"

    xml_full_string =   xml_text_header + xml_det_header + \
                        xml_text_siteId + \
                        xml_text_chNum + \
                        xml_text_detNum + \
                        xml_text_status + \
                        xml_text_distance + \
                        xml_text_btAmt + \
                        xml_det_tail + xml_text_tail 

    g_xml_text[int(ch_num)-1][int(det_num)-1] = xml_full_string

    return xml_full_string

#Serial Port Initialize
def serial_init(serial_ch):
    BAUDRATE = 38400
    global g_serial_port
    g_serial_port[serial_ch] = serial.Serial(SERIALPORT[serial_ch], BAUDRATE)
    g_serial_port[serial_ch].bytesize = serial.EIGHTBITS
    g_serial_port[serial_ch].parity = serial.PARITY_NONE
    g_serial_port[serial_ch].stopbit = serial.STOPBITS_ONE
    g_serial_port[serial_ch].timeout = 2
    g_serial_port[serial_ch].xonxoff = False
    g_serial_port[serial_ch].rtscts = False
    g_serial_port[serial_ch].dsrdtr = False
    g_serial_port[serial_ch].writeTimeout = 0

    try:
        g_serial_port[serial_ch].open()

    except Exception as e:
        print ("Exception: Opening serial port : " + str(e))

#Serial Port Close
def serial_close(serial_ch):
    g_serial_port[serial_ch].close()

#Init Status value
def clear_status_val(ch_num):
    global g_status_val
    
    for i in range(0, 5):  # max 5 detector per channel
        g_status_val[ch_num][i] = "2"

#Compare Status Change
def check_status_change(ch_num):
    global g_status_val
    global g_status_saved_val

    if g_status_val[ch_num] == g_status_saved_val[ch_num] :
        return 0        #Same Status
    else:
        g_status_saved_val[ch_num] = g_status_val[ch_num][:]
        return 1        #Status Change

### Check Integer string
def is_integer(n) :
    try :
        float(n)
    except ValueError:
        return False
    else:
        return float(n).is_integer()

### check data format integrity
def check_integrity(data):

    if(len(data) != 26) :
        print ("Serial Data Length Check Fail")
        return False
    if ((data[3] != ",") or (data[6] != ",") or (data[17] != ",") or (data[21] != ".")) :
        print ("Fail on Seperator")
        return False
    if ((data[0:2] != "CH") or (is_integer(data[2]) != True)) :
        print ("Channel string Check Fail")
        return False
    if ((int(data[2]) != 3) and (int(data[2]) != 4)) :
        print ("Channel number Check Fail")
    if (is_integer(data[4:6]) != True) :
        print ("Detector Number is not Integer")
        return False
    if ((int(data[4:6]) < 1) or (int(data[4:6]) > 10)) :
        print ("Detector Number range is over")
        return False
    if (is_integer(data[7:17]) != True) :
        print ("Distance Number is not Integer")
        return False
    if ((is_integer(data[18:21]) != True) or (is_integer(data[22:24]) != True)) :
        print ("Voltage Number is not Integer")
        return False

    return True


#Get Sensor data and store global variable
def get_sensor_data(serial_ch, ch_num):
    global g_serial_port
    global g_distance_val
    global g_volt_val
    global g_status_val
    global g_status_saved_val
    global g_xml_send

    if g_serial_port[serial_ch].isOpen():
        try:
            g_serial_port[serial_ch].flushInput()
            g_serial_port[serial_ch].flushOutput()

            double_check_count = 0

            while True:
                cmd_ch = "0" + str(ch_num + 2)      #CH3 is first ch(ch_num = 1)
                serial_cmd = "01," + cmd_ch + "\r\n"
                print serial_cmd

                g_serial_port[serial_ch].write(serial_cmd.encode('ascii'))
                ret = g_serial_port[serial_ch].readline().decode('ascii')
                print ret

                #if Not Response during timeout, then exit
                if ret == "" :
                    break

                # Check Data Integrity
                if (check_integrity(ret) == False):
                    print ("Data Integrity Error")
                    break

                #ch_num = ret.split(',')[0]
                det_num = ret.split(',')[1]
                lc_hz = ret.split(',')[2]
                volt = ret.split(',')[3]

                #eliminate string first "0"
                ch_num_int = int(ch_num) + serial_ch*2  #convert sting to int(2ch per port)
                ch_num_str = str(ch_num_int)            #convert int to string

                #eliminate string first "0"
                det_num_int = int(det_num)  #convert sting to int
                det_num_str = str(det_num_int)  #convert int to string

                #Sometimes Get Error    2020/6/29
                if det_num_int > 5 or det_num_int < 1:
                    print "Serial Return Value Error(det_num):", ret
                    break


                #eliminate string first "0"
                volt_flt = float(volt)#convert sting to int
                volt_str = str(volt_flt)  #convert int to string
                g_volt_val[ch_num_int-1][det_num_int-1] = volt_str

                #eliminate string first "0"
                lc_hz = int(lc_hz)  #convert sting to int

                distance = get_distance(lc_hz)
                distance_str = str(distance)
                g_distance_val[ch_num_int-1][det_num_int-1] = distance_str

                g_status_val[ch_num_int-1][det_num_int-1] = "1" #set status "1" for valid detector, channel
                print "serial :[", serial_ch, "]", "ch_num : ", ch_num_int-1, " det_num : ", det_num_int-1, det_num_str

                if det_num_int > 0:
                    xml_full_string = make_xml_text(ch_num_str, det_num_str, distance_str, volt_str, "1")
                #print xml_full_string

                time.sleep(0.3)


                # Det Num == "1" is Last Data for each Detector (data order : 2,3,4,5,1 for 5 detector/ 2,3,1 for 3 detector)
                if det_num_int == 1 :   
                    double_check_count = double_check_count + 1
                    if double_check_count >= MAX_DOUBLE_CHECK :
                        if check_status_change(ch_num_int-1) == 1:          #if status change, xml transfer immediately
                            print ("                     ##### Status Change #####")
                            g_xml_send = 1
                        else:
                            print ("                     $$$$$ Same Status $$$$$")

                        clear_status_val(ch_num_int-1)                      #set all status to "2"

                        break       # det_num == 1 and count == MAX

        except Exception as e:
            print ("Error communicating...: " + str(e))
            time.sleep(1)
    else:
        print ("Cannot open serial port.")



# Main Routine Start
serial_init(0)
serial_init(1)
serial_init(2)
count = 0
g_xml_send = 0

#Init g_xml_text
for i in range(0, 6):
    for j in range(0, 5):
        make_xml_text(str(i+1), str(j+1), "0", "0", "2")

#max detector number = 5, read 5 times for each CH
while True:
    ##### ttyUSB0 #####
    get_sensor_data(0, 1)       #ttyUSB0 0.1sec x 5 det x 10 repeat = 5sec
    get_sensor_data(0, 2)       # 0.1sec x 5 det x 10 repeat = 5sec

    get_sensor_data(1, 1)       #ttyUSB1
    get_sensor_data(1, 2)

    get_sensor_data(2, 1)       #ttyUSB2
    get_sensor_data(2, 2)

    count = count + 1
    print count

    if count >= TimeInterval or g_xml_send == 1:
        print "########## URL1 ##########"

        for i in range(0, 6):  #max 6 channel
            for j in range(0, 5):  #5 detector
                try :
                    ret = requests.post(url, data = g_xml_text[i][j], headers=headers, verify=False, timeout=3)
                    ret.raise_for_status()
                except requests.exceptions.HTTPError as errh:
                    print "$$$$$$$$$$"
                    print "Http Error:", errh
                    print "$$$$$$$$$$"
                    break
                except requests.exceptions.ConnectionError as errc:
                    print "$$$$$$$$$$"
                    print "Error Connecting:", errc
                    print "$$$$$$$$$$"
                    break
                except requests.exceptions.Timeout as errt:
                    print "$$$$$$$$$$"
                    print "Timeout Error:", err
                    print "$$$$$$$$$$"
                    break
                except requests.exceptions.RequestException as err:
                    print "$$$$$$$$$$"
                    print "Oops: Something Else:", err
                    print "$$$$$$$$$$"
                    break

                print g_xml_text[i][j]
                print ret.text

        print "########## URL2 ##########"

        for i in range(0, 6):  #max 6 channel
            for j in range(0, 5):  #5 detector
                try :
                    ret = requests.post(url2, data = g_xml_text[i][j], headers=headers, verify=False, timeout=3)
                    ret.raise_for_status()
                except requests.exceptions.HTTPError as errh:
                    print "$$$$$$$$$$"
                    print "Http Error:", errh
                    print "$$$$$$$$$$"
                    break
                except requests.exceptions.ConnectionError as errc:
                    print "$$$$$$$$$$"
                    print "Error Connecting:", errc
                    print "$$$$$$$$$$"
                    break
                except requests.exceptions.Timeout as errt:
                    print "$$$$$$$$$$"
                    print "Timeout Error:", err
                    print "$$$$$$$$$$"
                    break
                except requests.exceptions.RequestException as err:
                    print "$$$$$$$$$$"
                    print "Oops: Something Else:", err
                    print "$$$$$$$$$$"
                    break

                print g_xml_text[i][j]
                print ret.text


        count = 0
        g_xml_send = 0

serial_close(0)
serial_close(1)
serial_close(2)

