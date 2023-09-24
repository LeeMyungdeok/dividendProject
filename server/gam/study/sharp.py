#sub 서버 연결
from sqlalchemy import select,insert
import mysql.connector
import pymysql
from sqlalchemy import create_engine,text

# from stock

import os.path
import json

from fastapi import FastAPI

import math
import numpy
import stockquery

# from stock import result as R

BASE_DIR = os.path.dirname(os.path.dirname(os.path.relpath("./")))
secret_file = os.path.join(BASE_DIR, '../secretsub.json')

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

def get_db_data():
    with engine.connect() as conn:
        result = conn.execute(text("select * from stock"))
        resultDict = []
        for row in result:
            resultDict.append({'기준일자':row.기준일자,'주식발행회사명':row.주식발행회사명,"주식일반배당률":row.주식일반배당률,'주식결산월일':row.주식결산월일})
    return resultDict


# fastapi로 전부다 select
@app.get('/selectall')
async def selectall():
    result = get_db_data()
    return result


if __name__=='__main__':
    get_db_data()