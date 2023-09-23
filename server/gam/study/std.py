import math
import numpy
from stockquery import Selectfs
from sharp import selectall
from sharp import get_db_data

from fastapi import FastAPI
#api
app=FastAPI()


# fastapi로 전부다 select
@app.get('/std')
async def std():
    stock=Selectfs()
    result=[]
    for i in stock:
        result.append(int(i['Close']))
    #numpy mean
    # mean = numpy.mean(result)
    # print(mean)

    # #numpy variation
    # var = numpy.var(result)
    # print(var)

    #numpy standard deviation
    std=numpy.std(result)
    print(std)

    return std


@app.get('/sharp')
async def divid(divid):
    di= await selectall()
    for i in di:
        if i['주식발행회사명']==divid:
            div=int(i['주식일반배당률'])
            
            std1 = await std()
            result = (div - 3.575) / std1
        
            return result


#모든 회사의 배당률에대한 sharp 비율 top3 뽑기
@app.get('/allsharp')
async def allsharp():
    di= get_db_data()
    allthing=[]
    for i in di:
        div1=float(i['주식일반배당률'])
        div=int(div1)
        std1 = await std()
        result = (div - 3.575) / std1
        allthing.append(result)
        
    return allthing