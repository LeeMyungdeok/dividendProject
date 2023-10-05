import FinanceDataReader as fdr
import pandas as pd
import json
import yfinance as yf
from time import sleep
import pandas as pd
import numpy as np
import requests, json, os.path, sqlalchemy, os, pymysql
import pymysql
import os.path
BASE_DIR = os.path.dirname(os.path.dirname(os.path.relpath("./")))
secret_file = os.path.join(BASE_DIR, 'secret.json')

with open(secret_file) as f:
    secrets = json.loads(f.read())

def get_secret(setting, secrets=secrets):
    try:
        return secrets[setting]
    except KeyError:
        errorMsg = "Set the {} environment variable.".format(setting)
        return errorMsg

# 주가 조회
def stoks():
    # MySQL 연결
    # HOSTNAME=get_secret("rds_endpoint")
    # USERNAME=get_secret("Mysql_Username")
    # PASSWORD=get_secret("rds_password")
    # DBNAME=get_secret("Mysql_DBname")

    HOSTNAME = get_secret("rds_endpoint")
    PORT = get_secret("Mysql_Port")
    USERNAME = get_secret("Mysql_Username")
    PASSWORD = get_secret("rds_password")
    DBNAME = get_secret("Mysql_DBname")

    engine = f'mysql+pymysql://{USERNAME}:{PASSWORD}@{HOSTNAME}:{PORT}/{DBNAME}'
    print('Connected to Mysql....')
    engine = sqlalchemy.create_engine(engine)
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.relpath("./")))
    ticker_file = os.path.join(BASE_DIR, 'tickers.json')


    # engine = sqlalchemy.create_engine(f'mysql+pymysql://{USERNAME}:{PASSWORD}@{HOSTNAME}/{DBNAME}')
    # print('Connected to Mysql....')
    # BASE_DIR = os.path.dirname(os.path.dirname(os.path.relpath("./")))
    # ticker_file = os.path.join(BASE_DIR, './tickers.json')
    
    with open(ticker_file) as f:
        ticker = json.loads(f.read())
        
    df_symbols = {}
    for symbol in range(0,len(ticker["Symbol"])):
        try:
            tickers = ticker["Symbol"][f"{symbol}"]
            df = fdr.DataReader(f'{tickers}', '2023-09-22', '2023-09-29')
            dfs = df["Adj Close"].values
            
            df_symbols[f"{tickers}"] = dfs
        except KeyError as K:
            print(f"{tickers} 이친구 에러입니다. : K")
            continue
        
    print(df_symbols)
    df = pd.DataFrame(data = df_symbols)
    print(df)
    sleep(1)
    df.to_sql('price', engine, if_exists='replace', index=False)
        
        # if symbol == 0:
        #     df.to_sql('price', engine, if_exists='replace', index=False)
        # else:
        #     df.to_sql('price', engine, if_exists='append', index=False)

      
stoks()