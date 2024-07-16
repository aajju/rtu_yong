import requests
import time


python_file = "inside_server.py"  

site_id_boryeong11 = "boryeong11"  # 보령 sk주유소
xml_ok_boryeong11 = (                 
    "xmlText=<XML>"
    "<detector>"
    "<siteId>%s</siteId>"
    "<chNum>1</chNum>"
    "<detNum>1</detNum>"
    "<status>1</status>"
    "<distance>0</distance>"
    "<btAmt>22.84</btAmt>"
    "</detector>"
    "<detector>"
    "<siteId>%s</siteId>"
    "<chNum>2</chNum>"
    "<detNum>1</detNum>"
    "<status>1</status>"
    "<distance>0</distance>"
    "<btAmt>22.84</btAmt>"
    "</detector>"
    "</XML>"
) % (site_id_boryeong11, site_id_boryeong11)


site_id_boryeong13 = "boryeong13"  # 보령 sk주유소
xml_ok_boryeong13 = (                 
    "xmlText=<XML>"
    "<detector>"
    "<siteId>%s</siteId>"
    "<chNum>1</chNum>"
    "<detNum>1</detNum>"
    "<status>1</status>"
    "<distance>0</distance>"
    "<btAmt>22.84</btAmt>"
    "</detector>"
    "<detector>"
    "<siteId>%s</siteId>"
    "<chNum>2</chNum>"
    "<detNum>1</detNum>"
    "<status>1</status>"
    "<distance>0</distance>"
    "<btAmt>22.84</btAmt>"
    "</detector>"
    "</XML>"
) % (site_id_boryeong13, site_id_boryeong13)



def send_data_to_server(data, site_id):
    url = 'http://3.38.180.149:8080/dtxiot/sensor/add'
    headers = {'Content-Type' : 'application/x-www-form-urlencoded'}
    
    time.sleep(3)

    try:
        response = requests.post(url, data=data, headers=headers, verify=False, timeout=3)
        if response.status_code == 200:
            print("데이터가 성공적으로 전송되었습니다. - "+site_id)
        else:
            print("데이터 전송에 실패했습니다. 상태 코드:", response.status_code)
    except Exception as e:
        print("에러 발생:", e)

if __name__ == "__main__":

    data_list = [(xml_ok_boryeong11, site_id_boryeong11), 
                 (xml_ok_boryeong13, site_id_boryeong13)]


    while True:
        for data in data_list:
            send_data_to_server(data[0], data[1])

        # send_data_to_server(xml_ok_boryeong11,site_id_boryeong11)
        
        time.sleep(60*5)
        # time.sleep(60*60*3.5)  # 3h 30min마다 데이터를 전송하도록 설정합니다.

