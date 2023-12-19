#!/usr/bin/env python2
# -*- coding:utf-8 -*-

import requests
import serial
import time
import copy
import json
import re

from rtu_sms import send_sms

# 2022.8.22
# BECS, 3 Detectors, 1 channel

# 2023.3.21
# BECS, 7 Detectors, 5 channel

# 2023.5.17
# BECS, 7 Detectors, 5 channel
# add slack,  remove sms

# Detector Value
siteId_string = "move01"
#siteId_string = "bioptech01"
status_string = "1"
TimeInterval = 60 * 3 # 얼마인지 체크 필요

# Waiting count_times for valid status
MAX_DOUBLE_CHECK = 2   #60 
MAX_CH = 5
MAX_DET =7

# 인커밍 웹훅 URL
webhook_url = (
    "https://hooks.slack.com/services/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"
)

url = 'http://3.38.180.149:8080/dtxiot/sensor/add'
#headers = {'Content-Type' : 'multipart/form-data'}

#url = 'https://api.undercitysolution.com/Api/Sensor/getTest'
headers = {'Content-Type' : 'application/x-www-form-urlencoded'}

#url = 'http://192.168.100.22:8080/Api/Sensor/getTest'
#url = 'http://192.168.0.5:8080/Api/Sensor/getTest'
#url2 = 'http://192.168.0.6:8080/Api/Sensor/getTest'
url2 = 'https://api.undercitysolution.com/Api/Sensor/getTest'
#url = 'http://192.168.100.1:8080/Api/Sensor/getTest'

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
g_xml_text = [  ["ch1_det1", "ch1_det2", "ch1_det3", "ch1_det4", "ch1_det5", "ch1_det6", "ch1_det7"], 
                ["ch2_det1", "ch2_det2", "ch2_det3", "ch2_det4", "ch2_det5", "ch2_det6", "ch2_det7"], 
                ["ch3_det1", "ch3_det2", "ch3_det3", "ch3_det4", "ch3_det5", "ch3_det6", "ch3_det7"], 
                ["ch4_det1", "ch4_det2", "ch4_det3", "ch4_det4", "ch4_det5", "ch4_det6", "ch4_det7"], 
                ["ch5_det1", "ch5_det2", "ch5_det3", "ch5_det4", "ch5_det5", "ch5_det6", "ch5_det7"], 
               ] 

#CH x DET Distance Data
g_distance_val_old = [  ["ch1_det1", "ch1_det2", "ch1_det3", "ch1_det4", "ch1_det5", "ch1_det6", "ch1_det7"], 
                    ["ch2_det1", "ch2_det2", "ch2_det3", "ch2_det4", "ch2_det5", "ch2_det6", "ch2_det7"], 
                    ["ch3_det1", "ch3_det2", "ch3_det3", "ch3_det4", "ch3_det5", "ch3_det6", "ch3_det7"], 
                    ["ch4_det1", "ch4_det2", "ch4_det3", "ch4_det4", "ch4_det5", "ch4_det6", "ch4_det7"], 
                    ["ch5_det1", "ch5_det2", "ch5_det3", "ch5_det4", "ch5_det5", "ch5_det6", "ch5_det7"], 
                   ] 
g_distance_val = [  ["576", "610", "282", "350", "590", "838", "0"], 
                    ["576", "200", "282", "735", "590", "838", "0"], 
                    ["150", "610", "282", "735", "333", "838", "0"], 
                    ["576", "610", "282", "735", "590", "838", "0"], 
                    ["576", "610", "282", "735", "590", "838", "0"], 
                   ] 

#CH x DET Volt Data
g_volt_val = [  ["ch1_det1", "ch1_det2", "ch1_det3", "ch1_det4", "ch1_det5", "ch1_det6", "ch1_det7"], 
                ["ch2_det1", "ch2_det2", "ch2_det3", "ch2_det4", "ch2_det5", "ch2_det6", "ch2_det7"], 
                ["ch3_det1", "ch3_det2", "ch3_det3", "ch3_det4", "ch3_det5", "ch3_det6", "ch3_det7"], 
                ["ch4_det1", "ch4_det2", "ch4_det3", "ch4_det4", "ch4_det5", "ch4_det6", "ch4_det7"], 
                ["ch5_det1", "ch5_det2", "ch5_det3", "ch5_det4", "ch5_det5", "ch5_det6", "ch5_det7"], 
               ] 


#CH x DET DC Volt Data
g_dc_val =   [  ["ch1_det1", "ch1_det2", "ch1_det3", "ch1_det4", "ch1_det5", "ch1_det6", "ch1_det7"], 
                ["ch2_det1", "ch2_det2", "ch2_det3", "ch2_det4", "ch2_det5", "ch2_det6", "ch2_det7"], 
                ["ch3_det1", "ch3_det2", "ch3_det3", "ch3_det4", "ch3_det5", "ch3_det6", "ch3_det7"], 
                ["ch4_det1", "ch4_det2", "ch4_det3", "ch4_det4", "ch4_det5", "ch4_det6", "ch4_det7"], 
                ["ch5_det1", "ch5_det2", "ch5_det3", "ch5_det4", "ch5_det5", "ch5_det6", "ch5_det7"], 
               ] 

#CH x DET AC Volt Data
g_ac_val =   [  ["ch1_det1", "ch1_det2", "ch1_det3", "ch1_det4", "ch1_det5", "ch1_det6", "ch1_det7"], 
                ["ch2_det1", "ch2_det2", "ch2_det3", "ch2_det4", "ch2_det5", "ch2_det6", "ch2_det7"], 
                ["ch3_det1", "ch3_det2", "ch3_det3", "ch3_det4", "ch3_det5", "ch3_det6", "ch3_det7"], 
                ["ch4_det1", "ch4_det2", "ch4_det3", "ch4_det4", "ch4_det5", "ch4_det6", "ch4_det7"], 
                ["ch5_det1", "ch5_det2", "ch5_det3", "ch5_det4", "ch5_det5", "ch5_det6", "ch5_det7"], 
               ] 

#CH x DET Status Data
g_status_val = [["2", "2", "2", "2", "2", "2", "2"], 
                ["2", "2", "2", "2", "2", "2", "2"], 
                ["2", "2", "2", "2", "2", "2", "2"], 
                ["2", "2", "2", "2", "2", "2", "2"], 
                ["2", "2", "2", "2", "2", "2", "2"], 
               ] 

#CH x DET Status Data Saved
g_status_saved_val = [  ["2", "2", "2", "2", "2", "2", "2"], 
                        ["2", "2", "2", "2", "2", "2", "2"], 
                        ["2", "2", "2", "2", "2", "2", "2"], 
                        ["2", "2", "2", "2", "2", "2", "2"], 
                        ["2", "2", "2", "2", "2", "2", "2"], 
                        ] 



g_double_check_count = 0
g_prev_time = 0
g_cur_time = 0




# 주어진 문자열에서 XML 태그 내용을 추출하는 함수
def extract_value(xml_text, tag_name):
    pattern = "<{0}>(.*?)</{0}>".format(tag_name)
    match = re.findall(pattern, xml_text)
    return match


# 주어진 XML 텍스트에서 chNum, detNum, status 값을 추출하는 함수
def extract_data(xml_text):
    chnum_list = extract_value(xml_text, "chNum")
    detnum_list = extract_value(xml_text, "detNum")
    status_list = extract_value(xml_text, "status")
    return chnum_list, detnum_list, status_list


# 결과를 하나의 문자열로 만드는 함수
def format_output(chnum_list, detnum_list, status_list):
    output = ""
    for chnum, detnum, status in zip(chnum_list, detnum_list, status_list):
        output += "chNum: {0}\n".format(chnum)
        output += "detNum: {0}\n".format(detnum)
        output += "status: {0}\n".format(status)
        output += "--------------------\n"
    return output

# 주어진 XML 텍스트에서 status 값 중에 2가 있는지 체크하는 함수
def check_status_2(xml_text):
    status_list = extract_value(xml_text, "status")
    if "2" in status_list:
        return True
    else:
        return False



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
def make_xml_text(ch_num, det_num, distance, volt, dc, ac, status):
    global siteId_string, status_string
    global g_xml_text

    xml_text_siteId = "<siteId>" + siteId_string + "</siteId>"
    # First ch, det : ch_num = 1, det_num = 0 : Start (2021/7/29)
    xml_text_chNum = "<chNum>" + ch_num + "</chNum>"
    xml_text_detNum = "<detNum>" + det_num + "</detNum>"
    #xml_text_status = "<status>" + status_string + "</status>"
    xml_text_status = "<status>" + status + "</status>"
    xml_text_distance = "<distance>" + distance + "</distance>"
    xml_text_btAmt = "<btAmt>" + volt + "</btAmt>"
    xml_text_dc = "<dc>" + dc + "</dc>"
    xml_text_ac = "<ac>" + ac + "</ac>"

    xml_full_string =   xml_text_header + xml_det_header + \
                        xml_text_siteId + \
                        xml_text_chNum + \
                        xml_text_detNum + \
                        xml_text_status + \
                        xml_text_distance + \
                        xml_text_btAmt + \
                        xml_text_dc + \
                        xml_text_ac + \
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
    
    for i in range(0, MAX_DET):  # max 7 detector per channel
        g_status_val[ch_num][i] = "2"

#Compare Status Change
def check_status_change(ch_num):
    global g_status_val
    global g_status_saved_val

    if g_status_val[ch_num] == g_status_saved_val[ch_num] :
        return 0        #Same Status
    else:
        g_status_saved_val[ch_num] = g_status_val[ch_num][:]
        #g_status_saved_val[ch_num] = copy.deepcopy(g_status_val[ch_num][:])
        return 1        #Status Change



#Init g_xml_text
def clear_xml_text():
    for i in range(0, MAX_CH):
        for j in range(0, MAX_DET):
            make_xml_text(str(i+1), str(j+1), "0", "0", "0", "0", "2")
    
    print ("1111111111111111111111111111111111111111111111111")
    print ("&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&")
    print ("&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&")


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

    #if(len(data) != 26) :  #ORG Detector Data
    if(len(data) != 41) :   #New Becs Detector Data Added(Volotage Level) 2022.9.29
        print ("Serial Data Length Check Fail")
        return False
    if ((data[3] != ",") or (data[6] != ",") or (data[17] != ",") or (data[21] != ".")) :
        print ("Fail on Seperator")
        return False
    if ((data[0:2] != "CH") or (is_integer(data[2]) != True)) :
        print ("Channel string Check Fail")
        return False
    #if ((int(data[2]) != 3) and (int(data[2]) != 4)) :
    if ((int(data[2]) < 0) and (int(data[2]) > 5)) : # for BECS (channel 0 to 5)
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
    global g_dc_val
    global g_ac_val
    global g_status_val
    global g_status_saved_val
    global g_xml_send
    global g_double_check_count


    if g_serial_port[serial_ch].isOpen():
        try:
            g_serial_port[serial_ch].flushInput()
            g_serial_port[serial_ch].flushOutput()

            local_count = 0

            while True:
                #cmd_ch = "0" + str(ch_num + 2)          #CH3 is first ch(ch_num = 1) for JNC
                #serial_cmd = "01," + cmd_ch + "\r\n"    # for JNC
                cmd_ch = "0" + str(ch_num)              # CH1 is first ch for BECS
                serial_cmd = "01," + cmd_ch + "\r\n"    # For BECS 2 detector
                #print serial_cmd

                g_serial_port[serial_ch].write(serial_cmd.encode('ascii'))
                time.sleep(1.0)     # 2022.10.6 Detector Halt after 1 day
                ret = g_serial_port[serial_ch].readline().decode('ascii')
                print ("get_sensor_data() : ret --> " + ret)

                #if Not Response during timeout, then exit
                if ret == "" :
                    time.sleep(0.5)
                    local_count = local_count + 1
                    print ("Not response : "+str(local_count))
                    if (local_count >= 10):
                        break
                    continue

                # Check Data Integrity
                if (check_integrity(ret) == False):
                    #print ("Data Integrity Error")
                    time.sleep(0.5)
                    continue

                #ch_num = ret.split(',')[0]
                det_num = ret.split(',')[1]
                lc_hz = ret.split(',')[2]
                volt = ret.split(',')[3]
                # add 2023.3.8 ac & dc voltage
                dc_val = ret.split(',')[4]
                ac_val = ret.split(',')[5]

                #eliminate string first "0"
                #ch_num_int = int(ch_num) + serial_ch*2  #convert string to int(2ch per port)
                ch_num_int = int(ch_num)  #convert string to int(2ch per port)
                ch_num_str = str(ch_num_int)            #convert int to string

                #eliminate string first "0"
                det_num_int = int(det_num)  #convert sting to int
                det_num_str = str(det_num_int)  #convert int to string

                #Sometimes Get Error    2020/6/29
                if det_num_int > MAX_DET or det_num_int < 1: # for BECS 7 Detector
                    print "Serial Return Value Error(det_num):", ret
                    time.sleep(0.5)
                    continue


                #eliminate string first "0"
                volt_flt = float(volt)#convert sting to int
                volt_str = str(volt_flt)  #convert int to string
                g_volt_val[ch_num_int-1][det_num_int-1] = volt_str

                # add 2023.3.8 dc & ac voltage
                ac_flt = float(ac_val)
                ac_str = str(ac_flt)
                dc_flt = float(dc_val)
                dc_str = str(dc_flt)
                g_dc_val[ch_num_int-1][det_num_int-1] = dc_str
                g_ac_val[ch_num_int-1][det_num_int-1] = ac_str

                #eliminate string first "0"
                lc_hz = int(float(lc_hz))  #convert sting to int

                distance = get_distance(lc_hz)
                #distance_str = str(distance) # for JNC
                distance_str = str(lc_hz) # for BECS
                
                # Set Default Value (bioptech 2023.4.18)
                distance_str = g_distance_val[ch_num_int-1][det_num_int-1]

                
                g_distance_val[ch_num_int-1][det_num_int-1] = distance_str

                g_status_val[ch_num_int-1][det_num_int-1] = "1" #set status "1" for valid detector, channel


                #print "serial :[", serial_ch, "], ", "ch_num : ", ch_num_int-1, ", det_num : ", det_num_int-1, ", det_str : ", det_num_str

                #ch_num = 1, det_num = 0 : Start
                if det_num_int > 0:
                    make_xml_text(ch_num_str, det_num_str, distance_str, volt_str, dc_str, ac_str, "1")

                time.sleep(0.3)

                # Det Num == "1" is Last Data for each Detector (data order : 2,3,4,5,1 for 5 detector/ 2,3,1 for 3 detector)
                if det_num_int == 1 :
                    g_double_check_count = g_double_check_count + 1

                    if g_double_check_count >= MAX_DOUBLE_CHECK :
                        if check_status_change(ch_num_int-1) == 1:          #if status change, xml transfer immediately
                            print ("CH : "+ch_num_str+"   ##### Status Change #####")
                            g_xml_send = 1
                        else:
                            print ("                     $$$$$ Same Status $$$$$")

                        clear_status_val(ch_num_int-1)                      #set all status to "2"
                        g_double_check_count = 0

                        break       # det_num == 1 and count == MAX


        except Exception as e:
            print ("Error communicating...: " + str(e))
            time.sleep(1)
    else:
        print ("Cannot open serial port.")



# Main Routine Start
serial_init(0)
#serial_init(1)
#serial_init(2)
count = 0
g_xml_send = 0
g_prev_time = time.time()


clear_xml_text()

#max detector number = 7, read 5 times for each CH
while True:
    ##### ttyUSB0 #####
    ### for BECS
    get_sensor_data(0, 1)       #ttyUSB0 0.1sec x 5 det x 10 repeat = 5sec
    get_sensor_data(0, 2)       # 0.1sec x 5 det x 10 repeat = 5sec
    get_sensor_data(0, 3)       # 0.1sec x 5 det x 10 repeat = 5sec
    get_sensor_data(0, 4)       # 0.1sec x 5 det x 10 repeat = 5sec
    get_sensor_data(0, 5)       # 0.1sec x 5 det x 10 repeat = 5sec
    #get_sensor_data(0, 6)       # 0.1sec x 5 det x 10 repeat = 5sec

    ### for JNC
    #get_sensor_data(0, 1)       #ttyUSB0 COM3 for JNC
    #get_sensor_data(0, 2)       #ttyUSB0 COM4 for JNC

    #get_sensor_data(1, 1)       #ttyUSB1
    #get_sensor_data(1, 2)

    #get_sensor_data(2, 1)       #ttyUSB2
    #get_sensor_data(2, 2)

    count = count + 1
    print ("################################################")
    print ("main loop count : " + str(count))
    print ("################################################")

    # Time Check
    g_cur_time = time.time()
    # if( (g_cur_time - g_prev_time) > (60*60*24) ):
    if( (g_cur_time - g_prev_time) > (60*60*24) ):
        print ("Reset Timer")
        # 보낼 메시지
        payload = {
            "attachments": [
                {
                    "color": "#0000FF",  # 색상을 지정합니다. 여기서는 파란색으로 지정합니다.
                    "title": "RTU ALIVE - 남양주테스트 장비",
                    "text": time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(g_cur_time)),
                }
            ]
        }
        # JSON으로 변환하여 POST 요청 보내기
        response = requests.post(
            webhook_url, data=json.dumps(payload), headers={"Content-Type": "application/json"}
        )

        # 요청 결과 확인하기
        if response.status_code != 200:
            raise ValueError(
                "Request to Slack returned an error " + response.status_code + " " +response.text
            )  

        # send_sms("RTU Alive")
        g_prev_time = copy.deepcopy(g_cur_time)
    else :
        print ("TIME : ", str(g_cur_time - g_prev_time))


    # 주기적으로 서버에 데이터 전송  (슬랙 X)
    if count >= TimeInterval:
        print "########## URL1 - only server ##########"

        #for i in range(0, 1):  #max 1 channel
        for i in range(0, MAX_CH):  #max 5 channel
            #for j in range(0, 3):  #max 3 detector
            
            for j in range(0, MAX_DET):  #max 7 detector
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
                    print "Timeout Error:", errt
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

    # status 변화 감지시 데이터 전송 (서버 + 슬랙)
    if g_xml_send == 1:
        print "########## URL1 - server + slack ##########"

        #for i in range(0, 1):  #max 1 channel
        for i in range(0, MAX_CH):  #max 5 channel

            payload = {
                    "attachments": [
                        {
                            "color": "#FF0000",  # 색상을 지정합니다. 여기서는 빨간색으로 지정합니다.
                            "title": "이벤트 발생 - 남양주 테스트 장비",  # 장비별 타이틀 다르게
                            "text": g_xml_text[i][0] # 채널별 초기 세팅
                        }
                    ]
                 }
            
            for j in range(0, MAX_DET):  #max 7 detector
                try :
                    ret = requests.post(url, data = g_xml_text[i][j], headers=headers, verify=False, timeout=3)
                    ret.raise_for_status()
                    if j+1 < MAX_DET: 
                        payload["attachments"][0]["text"] += str(g_xml_text[i][j+1])

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
                    print "Timeout Error:", errt
                    print "$$$$$$$$$$"
                    break
                except requests.exceptions.RequestException as err:
                    print "$$$$$$$$$$"
                    print "Oops: Something Else:", err
                    print "$$$$$$$$$$"
                    break

                print g_xml_text[i][j]
                print ret.text

            # xml_text에서 데이터 추출
            chnum_list, detnum_list, status_list = extract_data(payload["attachments"][0]["text"])

            # 결과 출력
            result = format_output(chnum_list, detnum_list, status_list)
            
            # status 2 체크
            if check_status_2(payload["attachments"][0]["text"]):
                payload["attachments"][0]["text"] = result
                # JSON으로 변환하여 POST 요청 보내기
                response = requests.post(
                    webhook_url, data=json.dumps(payload), headers={"Content-Type": "application/json"}
                )
                # 요청 결과 확인하기
                if response.status_code != 200:
                    raise ValueError(
                        "Request to Slack returned an error " + response.status_code + " " +response.text
                    )   

        g_xml_send = 0

    #Clear xml_text(2021/7/28)
    clear_xml_text()
    #make_xml_text(str(i+1), str(j+1), "0", "0", "2")
    print("2222222222222222222222222222222222222222222222222")
    print("*************************************************")
    print("*************************************************")

#        print "########## URL2 ##########"
#
#        for i in range(0, 1):  #max 1 channel
#            for j in range(0, 7):  #7 detector
#                try :
#                    ret = requests.post(url2, data = g_xml_text[i][j], headers=headers, verify=False, timeout=3)
#                    ret.raise_for_status()
#                except requests.exceptions.HTTPError as errh:
#                    print "$$$$$$$$$$"
#                    print "Http Error:", errh
#                    print "$$$$$$$$$$"
#                    break
#                except requests.exceptions.ConnectionError as errc:
#                    print "$$$$$$$$$$"
#                    print "Error Connecting:", errc
#                    print "$$$$$$$$$$"
#                    break
#                except requests.exceptions.Timeout as errt:
#                    print "$$$$$$$$$$"
#                    print "Timeout Error:", err
#                    print "$$$$$$$$$$"
#                    break
#                except requests.exceptions.RequestException as err:
#                    print "$$$$$$$$$$"
#                    print "Oops: Something Else:", err
#                    print "$$$$$$$$$$"
#                    break
#
#                print g_xml_text[i][j]
#                print ret.text



serial_close(0)
#serial_close(1)
#serial_close(2)

