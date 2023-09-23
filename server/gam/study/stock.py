import pandas_datareader as pdr
from datetime import datetime
import mysql.connector
import yfinance as yf
import pandas as pd
import FinanceDataReader as fdr
import pymysql
from sqlalchemy import create_engine,text
import pandas as pd
import sqlalchemy
from sqlalchemy import select


import os.path
import json

import schedule
import time

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




def inserting(): 
    df_spx = fdr.StockListing('Kosdaq')
    df = df_spx[[ "Code","Name", "MarketId", "Dept", "Close"]]
    df.loc[:, "Date"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Create the SQLAlchemy engine object
    engine = create_engine(f'mysql+pymysql://{USERNAME}:{PASSWORD}@{HOSTNAME}/{DBNAME}')

   
    df.to_sql("stock", engine,if_exists='append' ,index=False)
    print('good')

inserting()
# #여기까지 db 넣기 python 실행하면 넣어짐.

#하루에 한번씩 실행
# schedule.every(10).seconds.do(inserting)
schedule.every(1).day.do(inserting)

# # step4.스캐쥴 시작 -> 매크로 처럼 돌리기
while True:
    schedule.run_pending()
    time.sleep(1)
    