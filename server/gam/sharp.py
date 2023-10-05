#%%
import mysql.connector
from sqlalchemy import create_engine,text
from sqlalchemy import select

import os.path
import json

import numpy as np

import matplotlib.pyplot as plt

import pandas as pd


BASE_DIR = os.path.dirname(os.path.dirname(os.path.relpath("./")))
secret_file = os.path.join(BASE_DIR, './secret.json')

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

# 배당률
def div():
    with engine.connect() as conn:
        # result = conn.execute(text("select dividendYield from stock where symbol='AAPL'"))
        result = conn.execute(text("select dividendYield from stock"))
        resultDict = []
        for row in result:
            resultDict.append(row[0])
        # print(resultDict)
    return resultDict

# div()

def price():
    with engine.connect() as conn:
        df1 = pd.read_sql_query("select AAPL from star", conn)
        df2 = pd.read_sql_query("select MCSF from star", conn)    
    ret1 = df1.pct_change()
    ret2 = df2.pct_change()
    # pct_change는 한 객체 내에서 행과 행의 차이를 현재값과의 백분율로 출력하는 메서드
    annual_ret1=ret1.mean() * 26 #종목의 1년간 수익률 평균(곱한 수는 data의 row수)
    daily_cov1 = ret1.cov() #연간 리스크, cov 함수를 이용해 일간변동률의 공분산
    annual_cov1 = daily_cov1 * 26 #(해당 기간동안) 리스크
    # print(annual_ret1)
    # print(daily_cov1)
    # print(annual_cov1)
    annual_ret2=ret2.mean() * 26
    daily_cov2 = ret2.cov()
    annual_cov2 = daily_cov2 * 26
    # print(annual_ret2)
    # print(daily_cov2)
    # print(annual_cov2)

    #두 주식에서 주식의 비율을 다르게 해서 100개의 포트폴리오 생성
    # 1. 수익률, 리스크, 비중 list 생성
    # 수익률 = port_ret
    # 리스크 = port_risk
    # 비  중 = port_weights
    port_ret =[]
    port_risk=[]
    port_weights=[]

    for i in range(100):
        # 2. 랜덤 숫자 3개생성 - 랜덤숫자 3개 합 = 1이 되게 생성
        weights1 = np.random.random(4)
        weights1 /= np.sum(weights1)
        weights2 = np.random.random(4)
        weights2 /= np.sum(weights2)

        # 3. 랜덤 생성된 종목별 비중 배열과 종목별 연간 수익률을 곱해 포트폴리오의 전체 수익률을 구현
        returns1=np.dot(weights1, annual_ret1)
        returns2=np.dot(weights2, annual_ret2)
        
        # 4. 종목별 연간공분산과 종목별 비중배열 곱하고, 다시 종목별 비중의 전치로 곱한다.
        # 결과값의 제곱근을 sqrt()함수로 구하면 해당 포트폴리오 전체 risk가 구해진다. 
        risk1 = np.sqrt(np.dot(weights1.T, np.dot(annual_cov1, weights1)))
        risk2= np.sqrt(np.dot(weights2.T, np.dot(annual_cov2, weights2)))

        # 5. 100개 포트폴리오의 수익률, 리스크, 종목별 비중을 각각 리스트에 추가한다.
        port_ret.append(returns1)
        port_risk.append(risk1)
        port_weights.append(weights1)
        port_ret.append(returns2)
        port_risk.append(risk2)
        port_weights.append(weights2)

        portfolio = {'Returns' : port_ret, 'Risk' : port_risk}
        for j, s in enumerate(stocks):
            # 6. portfolio 4종목의 가중치 weights를 1개씩 가져온다.
            portfolio[s] = [weight[j] for weight in port_weights]

        # 7. 최종 df는 시총 상위 5종목의 보유 비중에 따른 risk와 예상 수익률을 확인할 수 있다.
        df = pd.DataFrame(portfolio)
        df = df[['Returns', 'Risk'] + [s for s in stocks]]


        # 8. 효율적 투자선  그래프 그리기
        df.plot.scatter(x='Risk', y='Returns', figsize=(10,8), grid=True)
        plt.title('Efficient Frontier Graph')
        plt.xlabel('Risk')
        plt.ylabel('Expected Return')
        plt.show()



    #     result = conn.execute(text("select AAPL from price"))
    #     resultDict = [row[0] for row in result]
    #     # print(resultDict)
    # return resultDict

price()

# # standard deviation
# def std():
#     stock=price()
#     std1=np.std(stock)
#     print(std1)

#     return std1
    
# # std()

# #sharp 비율 구하기
# # def sharp():
# #     stdv=std()
# #     divv=div()
# #     divid=divv[0] #첫번째꺼
# #     result=(divid - 2 ) / stdv #2는 미국 국체
# #     print(result)
# #     return result

# # sharp()

# # 모든 divid에 대해서 sharp 비율 구하기
# def allsharp():
#     stdv=std()
#     sharplist=[]
#     for i in div():
#         result=round((i -2)/stdv,3)
#         sharplist.append(result)
#     # print(sharplist)
#     return sharplist

# allsharp()


# x= allsharp()
# y=range(len(allsharp()))


# plt.scatter(x,y)

# plt.xscale('log') 
# plt.yscale('log')

# plt.show()
# %%
