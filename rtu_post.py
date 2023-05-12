#!/usr/bin/env python2
# -*- coding: utf-8 -*-

import requests

# XML Text Header & Tail
xml_text_header = "xmlText=<XML>"
xml_text_tail = "</XML>"
xml_det_header = "<detector>"
xml_det_tail = "</detector>"

# Detector Value
siteId_string = "bioptech01"
chNum_string = "1"
detNum_string = "1"
status_string = "1"
distance_string = "0"
btAmt_string = "0"

# Detector Attribute
xml_text_siteId = "<siteId>" + siteId_string + "</siteId>"
xml_text_chNum = "<chNum>" + chNum_string + "</chNum>"
xml_text_detNum = "<detNum>" + detNum_string + "</detNum>"
xml_text_status = "<status>" + status_string + "</status>"
xml_text_distance = "<distance>" + distance_string + "</distance>"
xml_text_btAmt = "<btAmt>" + btAmt_string + "</btAmt>"

xml_full_string =   xml_text_header + xml_det_header + \
                    xml_text_siteId + \
                    xml_text_chNum + \
                    xml_text_detNum + \
                    xml_text_status + \
                    xml_text_distance + \
                    xml_text_btAmt + \
                    xml_det_tail + xml_text_tail 

#print xml_full_string

url = 'http://192.168.100.22:8080/Api/Sensor/getTest'
headers = {'Content-Type' : 'application/x-www-form-urlencoded'}

ret = requests.post(url, data = xml_full_string, headers=headers).text

print ret
