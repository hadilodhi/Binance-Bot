from binance.client import Client
import csv
import pandas as pd
#pd.options.mode.chained_assignment = None
from pandas import DataFrame
import json
import numpy as np
from datetime import datetime
import itertools


api_key = ""
api_secret = ""

client = Client(api_key, api_secret)
#candles = client.get_historical_klines("BTCUSDT", Client.KLINE_INTERVAL_30MINUTE, "24 Feb, 2021", "24 Apr, 2021")
#candles = client.get_klines(symbol='BTCUSDT', interval=Client.KLINE_INTERVAL_30MINUTE,limit=1000)
#closes = DataFrame(candles, columns=["OpenTime", "Open", "High", "Low", "Close","Volume", "CloseTime", "QAV", "NoTrades", "TBBAV", "TBQAV", "Ignore"])
r"""
closes.to_csv(r'C:\Users\Hadi Lodhi\Desktop\Javascript\Binance Bot\Data.csv',
              index=False, header=True)
"""



def MainLoop(a,b,c):
    closes = pd.read_csv(r'C:\Users\Hadi Lodhi\Desktop\Javascript\Binance Bot\Data.csv')
    closes["1stMA"] = closes["Close"].rolling(a).mean()
    closes["2ndMA"] = closes["Close"].rolling(b).mean()
    closes["3rdMA"] = closes["Close"].rolling(c).mean()
    closes = closes.dropna()


    def signal(x, y, z):
        if x > y and y > z:
            return "Buy"
        elif x < y and y < z:
            return "Sell"
        else:
            return "IDK"


    closes["Signal"] = np.vectorize(signal)(closes["1stMA"], closes["2ndMA"], closes["3rdMA"])
    closes["Consec"] = closes["Signal"] == closes.shift()["Signal"]
    closes["Change"] = closes["Close"].astype(float).pct_change()
    mask = closes.applymap(type) != bool
    d = {True: 'True', False: 'False'}
    closes = closes.where(mask, closes.replace(d))

    PorL = []
    Profit = 0
    TrailingSL = 0.02


    def Calc():
        SL = 0
        Price = closes["Open"].iloc[i+1]
        #print("Price = ", Price)
        for j in range(len(closes)-i):
            Close = closes["Close"].iloc[i+j]
            change = (float(Close)-float(Price))/float(Price)
            if x == "BUY":
                change = change
            elif x == "Sell":
                change = - change
            SL += change
            if SL > 0.0:
                SL = 0.0
            if x in closes["Signal"].iloc[i+j+1] and "False" in closes["Consec"].iloc[i+j+1]:
                Close = closes["Close"].iloc[i+j+1]
                PL = (float(Close)-float(Price))/float(Price)
                PL = PL
                #print("Close = ", closes["Close"].iloc[i+j])
                PorL.append(abs(PL))
                break
            elif SL < -TrailingSL:
                Close = closes["Close"].iloc[i+j]
                PL = (float(Close)-float(Price))/float(Price)
                #print("Close = ", closes["Close"].iloc[i+j])
                PorL.append(PL)
                break
            elif y in closes["Signal"].iloc[i+j]:
                Close = closes["Close"].iloc[i+j]
                PL = (float(Close)-float(Price))/float(Price)
                PorL.append(PL)
                break


    for i in range(len(closes)):
        if "Buy" in closes["Signal"].iloc[i] and "False" in closes["Consec"].iloc[i]:
            x = "Buy"
            y = "Sell"
            Calc()
        elif "Sell" in closes["Signal"].iloc[i] and "False" in closes["Consec"].iloc[i]:
            y = "Buy"
            x = "Sell"
            Calc()
        
    for element in range (0, len(PorL)):
        Profit = Profit + PorL[element]    
    Profit = Profit *100
    Final = [element * 100 for element in PorL]
    #emas = "EMA1 = " + str(a) + " EMA2 = " + str(b) + " EMA3 = " + str(c)
    #print(emas)
    #print(Final)
    print("Profit = ", "%.2f" % Profit, "%")
    timestamp = closes["OpenTime"].iloc[1] / 1000
    value = datetime.fromtimestamp(timestamp)
    DATATA = [a,b,c,Profit]
    return DATATA
    #print("Data Start Time = ", f"{value:%Y-%m-%d %H:%M:%S}")

    #output = closes[((closes["Signal"] == "Buy") | (closes["Signal"] == "Sell")) & (closes["Consec"] == "False")]
    #print(output[["Close", "Signal"]])

    #closes = closes[["OpenTime","Close","Open","Change","Signal","Consec"]]
    #closes.to_csv(r'C:\Users\Hadi Lodhi\Desktop\Javascript\Binance Bot\Output.csv',
                #index=False, header=True)

Meh = []
DATATA = []
n = 20
for l in range (20,25):
    a = l
    for m in range (40,50):
        b = m
        for o in range (90,110):
            c = o
            print ("[",a,b,c,"]")
            Meh.append(MainLoop(a,b,c))
df2 = DataFrame(Meh,columns = ["1stMA","2ndMA","3rdMA","Profit"])
print(df2)
df2.to_csv(r'C:\Users\Hadi Lodhi\Desktop\Javascript\Binance Bot\MAs.csv',index=False, header=True)
