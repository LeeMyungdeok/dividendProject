import requests, json, os.path, sqlalchemy, os
from sqlalchemy import create_engine
import pandas as pd

BASE_DIR = os.path.dirname(os.path.dirname(os.path.relpath("./")))
secret_file = os.path.join(BASE_DIR, '../secret.json')

with open(secret_file) as f:
    secrets = json.loads(f.read())

def get_secret(setting, secrets=secrets):
    try:
        return secrets[setting]
    except KeyError:
        errorMsg = "Set the {} environment variable.".format(setting)
        return errorMsg

# MySQL 연결
HOSTNAME = get_secret("Mysql_Hostname")
PORT = get_secret("Mysql_Port")
USERNAME = get_secret("Mysql_Username")
PASSWORD = get_secret("Mysql_Password")
DBNAME = get_secret("Mysql_DBname")

DB_URL = f'mysql+pymysql://{USERNAME}:{PASSWORD}@{HOSTNAME}:{PORT}/{DBNAME}'
print('Connected to Mysql....')

engine = create_engine(DB_URL)


def getRequestUrl(url):
    res = requests.get(url)
    try:
        if res.status_code == 200:
            return res
    except Exception as e:
        print("[%s] Error for URL : %s" % (datetime.datetime.now(), url))
        return None

def getdata():
    end_point = 'https://opendart.fss.or.kr/api/fnlttXbrl.xml'

    parameters = ''
    parameters += "?crtfc_key=" +get_secret("finan_apiKey")
    parameters += "&rcept_no=20190401004781"
    parameters += "&reprt_code=11013" #1분기 : 11013, 반기: 11012 3분기:11014 사업 : 11011
    
    url = end_point + parameters
    
    res = getRequestUrl(url)
    if (res == None):
        return None
    else:
        dict_json = json.loads(res.text) 
        return dict_json

def NewData():
    jsonResult = []
    pageNo = 1  
    numOfRows = 10
    nPage = 0
    while(True):
        print('pageNo : %d, nPage : %d' % (pageNo, nPage))
        jsonData = getdata(numOfRows, pageNo)

        if (jsonData['result']['']['resultCode'] == '00'):
            totalCount = jsonData['response']['body']['totalCount']


            for item in jsonData['response']['body']['items']['item']:
                jsonResult.append(item)

            if totalCount == 0:
                break

            # nPage = math.ceil(totalCount / numOfRows)
            # if (pageNo == 10):  
            #     break  

            # pageNo += 1
        else :
            break
    return jsonResult

stock = getdata()
print(stock)