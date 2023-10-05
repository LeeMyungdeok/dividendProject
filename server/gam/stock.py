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


# 기업 티커 가져오기
def getTicker():
    nasdaq = fdr.StockListing('NASDAQ')
    nasdaq['Indexes'] = 'NASDAQ'
    nasdaq.to_json('tickers.json', orient = 'columns', indent = 4)
    print('나스닥 :', type(nasdaq))


def dividend():
    # MySQL 연결
    HOSTNAME=get_secret("rds_endpoint")
    USERNAME=get_secret("Mysql_Username")
    PASSWORD=get_secret("rds_password")
    DBNAME=get_secret("Mysql_DBname")

    engine = sqlalchemy.create_engine(f'mysql+pymysql://{USERNAME}:{PASSWORD}@{HOSTNAME}/{DBNAME}')
    print('Connected to Mysql....')
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.relpath("./")))
    ticker_file = os.path.join(BASE_DIR, './tickers.json')
    
    with open(ticker_file) as f:
        ticker = json.loads(f.read())

    stock = {}
    cnt = 0
    for symbol in range(0,len(ticker["Symbol"])):
        tickers = ticker["Symbol"][f"{symbol}"]
        name = ticker["Name"][f"{symbol}"]
        datas = yf.Ticker(f'{tickers}')
        data = datas.info
        print(f"Symbol : {tickers}")
        try:
            stock["dividendYield"] = float(data['dividendYield']) * 100
            print(f"div : {float(data['dividendYield']) * 100 }")
        except:
            stock["dividendYield"] = 0.0
        try:
            
            stock["symbol"] = tickers
            stock["name"] = name
            print(stock)
            df = pd.DataFrame.from_records([stock])
            print(df)
            if cnt == 0 :
                df.to_sql('stock', engine, if_exists='replace', index=False)
            else:
                df.to_sql('stock', engine, if_exists='append', index=False)

            stock = {}
            cnt = 1
        except :
            print(f"{tickers} 이친구 에러입니다.")
            
        sleep(1)

dividend()

 
# 주가 조회
def stoks():
    # MySQL 연결
    HOSTNAME=get_secret("rds_endpoint")
    USERNAME=get_secret("Mysql_Username")
    PASSWORD=get_secret("rds_password")
    DBNAME=get_secret("Mysql_DBname")

    engine = sqlalchemy.create_engine(f'mysql+pymysql://{USERNAME}:{PASSWORD}@{HOSTNAME}/{DBNAME}')
    print('Connected to Mysql....')
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.relpath("./")))
    ticker_file = os.path.join(BASE_DIR, './tickers.json')
    
    with open(ticker_file) as f:
        ticker = json.loads(f.read())
        
    df_symbols = {}
    for symbol in range(0,len(ticker["Symbol"])):
        try:
            tickers = ticker["Symbol"][f"{symbol}"]
            df = fdr.DataReader(f'{tickers}', '2022-09-22', '2023-10-01')
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

      
# stoks()