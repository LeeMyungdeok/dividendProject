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


with engine.connect() as conn:
    df = pd.read_sql_query("select * from star", conn)
    columns= conn.execute(text("SELECT COUNT(*) FROM information_schema.columns WHERE table_name='star'")).scalar(); 
    rows= conn.execute(text("SELECT COUNT(*) AS row_count FROM star")).scalar();   
    stocks1=conn.execute(text("SELECT * FROM information_schema.columns WHERE table_name='star' ORDER BY ordinal_position"));
ret= df.pct_change()
# pct_change는 한 객체 내에서 행과 행의 차이를 현재값과의 백분율로 출력하는 메서드
annual_ret=ret.mean() * rows #종목의 1년간 수익률 평균(곱한 수는 data의 row수)
daily_cov = ret.cov() #해당기간동안 리스크, cov 함수를 이용해 일간변동률의 공분산
annual_cov = daily_cov * rows #(해당 기간동안) 리스크
print(annual_ret)
print(daily_cov)
print(annual_cov)
# print(columns) #컬럼갯수
# print(rows) #가로행 수


#두 주식에서 주식의 비율을 다르게 해서 100개의 포트폴리오 생성
# 1. 수익률, 리스크, 비중 list 생성
# 수익률 = port_ret
# 리스크 = port_risk
# 비  중 = port_weights
port_ret =[]
port_risk=[]
port_weights=[]
# 샤프지수 추가
shape_ratio = []

#column을 리스트 내에 나열

stocks=[row[3] for row in stocks1]
# print(stocks)

for i in range(20000):
    # 2. 랜덤 숫자 컬럼수 개생성 - 랜덤숫자 컬럼수 개 합 = 1이 되게 생성
    weights = np.random.random(columns)
    weights /= np.sum(weights)

    # 3. 랜덤 생성된 종목별 비중 배열과 종목별 연간 수익률을 곱해 포트폴리오의 전체 수익률을 구현
    returns=np.dot(weights, annual_ret)
    
    # 4. 종목별 연간공분산과 종목별 비중배열 곱하고, 다시 종목별 비중의 전치로 곱한다.
    # 결과값의 제곱근을 sqrt()함수로 구하면 해당 포트폴리오 전체 risk가 구해진다. 
    risk = np.sqrt(np.dot(weights.T, np.dot(annual_cov, weights)))

    # 5. 100개 포트폴리오의 수익률, 리스크, 종목별 비중을 각각 리스트에 추가한다.
    port_ret.append(returns)
    port_risk.append(risk)
    port_weights.append(weights)
    shape_ratio.append(returns/risk)



portfolio = {'Returns' : port_ret, 'Risk' : port_risk, 'Shape' : shape_ratio}
for j, s in enumerate(stocks):
    # 6. portfolio 4종목의 가중치 weights를 1개씩 가져온다.
    portfolio[s] = [weight[j] for weight in port_weights]

# 7. 최종 df는 시총 상위 5종목의 보유 비중에 따른 risk와 예상 수익률을 확인할 수 있다.
df = pd.DataFrame(portfolio)
df = df[['Returns', 'Risk','Shape'] + [s for s in stocks]]


# # 8. 효율적 투자선  그래프 그리기
# df.plot.scatter(x='Risk', y='Returns', figsize=(10,8), grid=True)
# plt.title('Efficient Frontier Graph')
# plt.xlabel('Risk')
# plt.ylabel('Expected Return')
# plt.show()

# 여기서부터는 shape 추가된 포스팅 보고서 추가된 내용
# 8. 샤프지수로 위험단위당 예측 수익률이 가장 높은 포트폴리오 구하기
# 샤프지수 칼럼에서 가장 높은 샤프지수 구하기
max_shape = df.loc[df['Shape'] == df['Shape'].max()]
print(max_shape)

# 리스크칼럼에서 가장 낮은 리스크 구하기
min_risk = df.loc[df['Risk'] == df['Risk'].min()]
print(min_risk)

# 샤프지수 그래프 그리기
df.plot.scatter(x='Risk', y='Returns', c='Shape', cmap='viridis', edgecolors='k', figsize=(10,8), grid=True)
plt.scatter(x=max_shape['Risk'], y=max_shape['Returns'], c='r', marker='X', s=300)
plt.scatter(x=min_risk['Risk'], y=min_risk['Returns'], c='r', marker='X', s=200)
plt.title('Portfolio Optimization')
plt.xlabel('Risk')
plt.ylabel('Expected Return')
plt.show()




save_path =f'./images/'
filename=f'sharp2.png'
plt.savefig(save_path+filename, dpi=400, bbox_inches='tight')