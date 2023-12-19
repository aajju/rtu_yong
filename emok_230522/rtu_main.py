#!/usr/bin/env python2
# -*- coding:utf-8 -*-

import requests
import serial
import time
import copy
import json
import re

# 2023.5.17
# add slack,  remove sms

# 2023.5.22
# BECS, 2 Detectors, 2 channel

# Detector Value
TimeInterval = 60 * 3 # 얼마인지 체크 필요

# Waiting count_times for valid status
MAX_DOUBLE_CHECK = 2   #60 
MAX_CH = 2  #최대채널
MAX_DET =2  #최대장비


#LC Tlanslation
ref_hz = (105920, 75410, 62080, 54850, 50280, 46840, 44380, 42440, 40930, 39610, 38480, 37530, 36720, 36000, 35300, 35040)

SERIALPORT = ("/dev/ttyUSB0", "/dev/ttyUSB1", "/dev/ttyUSB2")   #tuple
g_serial_port = ["ser1","ser2","ser3"]                          #list

#CH x DET XML TEXT
g_xml_text = [  ["ch1_det1", "ch1_det2"], 
                ["ch2_det1", "ch2_det2"], ] 

#CH x DET Distance Data
g_distance_val_old = [  ["ch1_det1", "ch1_det2"], 
                        ["ch2_det1", "ch2_det2"], ] 

g_distance_val = [  ["0", "0"], 
                    ["0", "0"], 
                   ] 

#CH x DET Volt Data
g_volt_val = [  ["ch1_det1", "ch1_det2"], 
                ["ch2_det1", "ch2_det2"], ] 


#CH x DET DC Volt Data
g_dc_val =   [  ["ch1_det1", "ch1_det2"], 
                ["ch2_det1", "ch2_det2"],  ] 

#CH x DET AC Volt Data
g_ac_val =   [  ["ch1_det1", "ch1_det2"], 
                ["ch2_det1", "ch2_det2"],  ] 

#CH x DET Status Data
g_status_val = [["2", "2", ], 
                ["2", "2", ], 
               ] 

#CH x DET Status Data Saved
g_status_saved_val = [["2", "2", ], 
                      ["2", "2", ], 
               ] 


g_prev_slack = ["x","x"]  #채널 개수만큼 "x" 추가

g_double_check_count = 0
g_prev_time = 0
g_cur_time = 0


def extract_volt_from_xml(prev_slack):
    volts = []  # 전압 값을 저장할 리스트
    devices = []  # 장비(detNum) 값을 저장할 리스트

    if prev_slack:  # prev_slack이 비어있지 않은 경우에만 처리
        first_slack_msg = prev_slack[0]  # 첫 번째 메시지만 처리

        lines = first_slack_msg.split("\n")  # 각 줄로 분리하여 처리

        for line in lines:
            if line.startswith("volt:"):
                volt = line.split(":")[1].strip()  # "volt:" 다음의 값을 추출하여 전압 값으로 저장
                volts.append(float(volt))  # 전압 값을 실수형으로 변환하여 리스트에 추가

            if line.startswith("detNum:"):
                detNum = line.split(":")[1].strip()  # "detNum:" 다음의 값을 추출하여 장비(detNum) 값으로 저장
                devices.append(int(detNum))  # 장비(detNum) 값을 정수형으로 변환하여 리스트에 추가

    return volts, devices

def send_slack(payload):
    webhook_url = "https://hooks.slack.com/services/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"
    response = requests.post(
        webhook_url, data=json.dumps(payload), headers={"Content-Type": "application/json"}
    )
    if response.status_code != 200:
        raise ValueError(f"Request to Slack returned an error {response.status_code}, {response.text}")


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
    volt_list = extract_value(xml_text, "btAmt")
    return chnum_list, detnum_list, status_list, volt_list


# 결과를 하나의 문자열로 만드는 함수
def format_output(chnum_list, detnum_list, status_list, volt_list):
    output = ""
    for chnum, detnum, status, volt in zip(chnum_list, detnum_list, status_list, volt_list):
        output += "chNum: {0}\n".format(chnum)
        output += "detNum: {0}\n".format(detnum)
        output += "status: {0}\n".format(status)
        output += "volt: {0}\n".format(volt)
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
    global g_xml_text

    xml_text_chNum = "<chNum>" + ch_num + "</chNum>"
    xml_text_detNum = "<detNum>" + det_num + "</detNum>"
    xml_text_status = "<status>" + status + "</status>"
    xml_text_distance = "<distance>" + distance + "</distance>"
    xml_text_btAmt = "<btAmt>" + volt + "</btAmt>"
    xml_text_dc = "<dc>" + dc + "</dc>"
    xml_text_ac = "<ac>" + ac + "</ac>"

    xml_full_string =   xml_text_chNum + \
                        xml_text_detNum + \
                        xml_text_status + \
                        xml_text_distance + \
                        xml_text_btAmt + \
                        xml_text_dc + \
                        xml_text_ac

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
                
                # # Set Default Value (bioptech 2023.4.18)
                # distance_str = g_distance_val[ch_num_int-1][det_num_int-1]

                
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
    # get_sensor_data(0, 3)       # 0.1sec x 5 det x 10 repeat = 5sec
    # get_sensor_data(0, 4)       # 0.1sec x 5 det x 10 repeat = 5sec
    # get_sensor_data(0, 5)       # 0.1sec x 5 det x 10 repeat = 5sec
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


    if( (g_cur_time - g_prev_time) > (60*6) ):  # 6분 주기로 보냄 (테스트용)
    # if( (g_cur_time - g_prev_time) > (60*60*4) ):  # 4시간 주기로 보냄
        print ("Reset Timer")

        # g_xml_text 변수로부터 필요한 정보 추출
        volts, devices = extract_volt_from_xml(g_prev_slack)  # 이전 Slack 메시지에서 전압 값을 추출

        text = "전압\n"
        for i, volt in enumerate(volts):
            device = devices[i]
            text += "장비 {}: {}\n".format(device, volt)

        payload = {
            "attachments": [
                {
                    "color": "#0000FF",  # 색상을 지정합니다. 여기서는 파란색으로 지정합니다.
                    "title": "RTU ALIVE - 이목지구 시공용",
                    "text": text,
                }
            ]
        }

        send_slack(payload)

        g_prev_time = copy.deepcopy(g_cur_time)
    else:
        print("TIME:", str(g_cur_time - g_prev_time))



    # status 변화 감지시 데이터 전송 
    if g_xml_send == 1:
        print "########## SEND slack ##########"

        for i in range(0, MAX_CH):  
            payload = {
                    "attachments": [
                        {
                            "color": "#FF0000",  # 색상을 지정합니다. 여기서는 빨간색으로 지정합니다.
                            "title": "이벤트 변경 - 이목지구 시공용",  # 장비별 타이틀 다르게
                            "text": g_xml_text[i][0] # 채널별 초기 세팅
                        }
                    ]
                 }
            
            for j in range(0, MAX_DET): 
                if j+1 < MAX_DET: 
                    payload["attachments"][0]["text"] += str(g_xml_text[i][j+1])

                print (g_xml_text[i][j])

    # xml_text_btAmt = "<btAmt>" + volt + "</btAmt>"


            # xml_text에서 데이터 추출
            chnum_list, detnum_list, status_list, volt_list = extract_data(payload["attachments"][0]["text"])

            # 결과 출력
            result = format_output(chnum_list, detnum_list, status_list, volt_list)
            
            if g_prev_slack[i] == result:
                continue
            elif g_prev_slack[i] == "x":
                g_prev_slack[i] = result
                continue
            else:
                payload["attachments"][0]["text"] = result
                send_slack(payload)
                g_prev_slack[i] = result


        g_xml_send = 0

    clear_xml_text()
    print("2222222222222222222222222222222222222222222222222")
    print("*************************************************")
    print("*************************************************")




serial_close(0)
#serial_close(1)
#serial_close(2)

