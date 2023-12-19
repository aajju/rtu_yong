xmlText=<XML>
<detector>
<siteId>siteId_string</siteId>
<chNum>ch_num</chNum>
<detNum>det_num</detNum>
<status>status</status>
<distance>distance</distance>
<btAmt>volt</btAmt>
<dc>dc</dc>
<ac>ac</ac>
</detector>
</XML>

"<detector>" + \
"<siteId>songpa01</siteId>" + \
"<chNum>1</chNum>" + \
"<detNum>1</detNum>" + \
"<status>1</status>" + \
"<distance>0</distance>" + \
"<btAmt>22.84</btAmt>" + \
"<dc>0</dc>" + \
"<ac>0</ac>" + \
"</detector>" + \
"<detector>" + \
"<siteId>songpa01</siteId>" + \
"<chNum>1</chNum>" + \
"<detNum>2</detNum>" + \
"<status>1</status>" + \
"<distance>0</distance>" + \
"<btAmt>22.84</btAmt>" + \
"<dc>0</dc>" + \
"<ac>0</ac>" + \
"</detector>" + \
"<detector>" + \
"<siteId>songpa01</siteId>" + \
"<chNum>1</chNum>" + \
"<detNum>1</detNum>" + \
"<status>3</status>" + \
"<distance>0</distance>" + \
"<btAmt>22.84</btAmt>" + \
"<dc>0</dc>" + \
"<ac>0</ac>" + \
"</detector>"



xml_det_header = "<detector>"
xml_det_tail = "</detector>"

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


xml_full_string =   xml_det_header + \
                    xml_text_siteId + \
                    xml_text_chNum + \
                    xml_text_detNum + \
                    xml_text_status + \
                    xml_text_distance + \
                    xml_text_btAmt + \
                    xml_text_dc + \
                    xml_text_ac + \
                    xml_det_tail

g_xml_text[int(ch_num)-1][int(det_num)-1] = xml_full_string