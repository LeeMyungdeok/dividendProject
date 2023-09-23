from sqlalchemy import select,insert
import mysql.connector
import pymysql
from sqlalchemy import create_engine,text

# from stock

import os.path
import json

from fastapi import FastAPI

# from stock import result as R

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

HOSTNAME=get_secret("rds_endpoint")
USERNAME=get_secret("Mysql_Username")
PASSWORD=get_secret("rds_password")
DBNAME=get_secret("Mysql_DBname")

engine = create_engine(f'mysql+pymysql://{USERNAME}:{PASSWORD}@{HOSTNAME}/{DBNAME}')

#api
app=FastAPI()

def Selectfs():
    with engine.connect() as conn:
        result = conn.execute(text("select * from stock"))
        resultDict = []
        for row in result:
            resultDict.append({"Code" : row.Code, "Name":row.Name, "MarketId" : row.MarketId, "Dept" : row.Dept, "Close": row.Close})
    return resultDict

# fastapi로 전부다 select
@app.get('/selectall')
async def selectall():
    result = Selectfs()
    return result


#일부 select - Name
@app.get('/selectname')
async def selectname(name:str):
    with engine.connect() as conn:
        result = conn.execute(text("select * from stock where Name='" + name + "'"))
        resultDict = []
        for row in result:
            resultDict.append({"Code" : row.Code, "Name":row.Name, "MarketId" : row.MarketId, "Dept" : row.Dept, "Close": row.Close,"Date":row.Date})
        print(resultDict)
    return resultDict

    
if __name__=="__main__":
    Selectfs()
