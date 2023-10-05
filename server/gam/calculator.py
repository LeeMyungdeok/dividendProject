# 복리계산기
#복리 계산 공식
# A = 초기 원금
# r = 이율 (이자율)
# n = 투자 기간
# A(1+r)^n

import math

# def cal(): 
#     start = int(input("초기금: "))
#     per = int(input("이율: "))/100
#     day = int(input("기간: "))

#     m =  start * ((1+per) **day)

#     print(round(m))

# cal()

start = int(input("초기금: "))
per = int(input("이율: "))/100
day = int(input("기간: "))

def calcul(start, per, day):
    m =  start * ((1+per) **day)

    print(round(m))

calcul(start,per,day)