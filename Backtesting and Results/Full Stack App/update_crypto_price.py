from binance.client import Client
import config
from pandas import DataFrame
import pandas as pd
import os
from datetime import date
from datetime import datetime
from dateutil.relativedelta import relativedelta
from tabulate import tabulate
import sqlite3

connection = sqlite3.connect('app.db')
connection.row_factory = sqlite3.Row
cursor = connection.cursor()

cwd = os.getcwd()
datadir = cwd + r"\Data.csv"

cursor.execute("SELECT opentime FROM crypto_price WHERE id = (SELECT MAX(id) FROM crypto_price)")
startdate = cursor.fetchall()
startdate = [startdate['opentime'] for startdate in startdate]
startdate = datetime.strptime(startdate[0], '%Y-%m-%d %H:%M:%S')
startdate = startdate.strftime("%d %b, %Y")

client = Client(config.API_KEY, config.API_SECRET)
#startdate = (date.today() - relativedelta(months=2)).strftime("%d %b, %Y")
enddate = date.today().strftime("%d %b, %Y")
#enddate = (date.today() - relativedelta(months=1)).strftime("%d %b, %Y")
print('For dates between', startdate, 'and' ,enddate)

cursor.execute("SELECT id, symbol from crypto")
rows = cursor.fetchall()
symbols = [row['symbol'] for row in rows]
crypto_ids = [row['id'] for row in rows]
for x in range(0,len(rows)):
    print('Updating Values for', symbols[x])
    candles = client.get_historical_klines(symbols[x], Client.KLINE_INTERVAL_30MINUTE, startdate, enddate)
    #candles = client.get_klines(symbol=symbols[x], interval=Client.KLINE_INTERVAL_30MINUTE,limit=1000)
    df = DataFrame(candles, columns=["Time", "Open", "High", "Low", "Close","Volume", "CloseTime", "QAV", "NofT", "TBBAV", "TBQAV", "Ignore"])
    df = df.drop(["CloseTime", "QAV", "NofT", "TBBAV", "TBQAV", "Ignore"], 1)
    df["Time"] = pd.to_datetime(df["Time"], unit='ms')
    for y in range(0,len(df)-1):
        cursor.execute("INSERT INTO crypto_price (crypto_id, opentime, open, high, low, close, volume) VALUES (?, ?, ?, ?, ?, ?, ?)", (crypto_ids[x], str(df["Time"].iloc[y]), df["Open"].iloc[y], df["High"].iloc[y], df["Low"].iloc[y], df["Close"].iloc[y], df["Volume"].iloc[y]))
        print('Added record for', df["Time"].iloc[y])
        #print(crypto_ids[x], df["Time"].iloc[y], df["Open"].iloc[y], df["High"].iloc[y], df["Low"].iloc[y], df["Close"].iloc[y], df["Volume"].iloc[y])
    #print(tabulate(df, headers='keys', tablefmt='psql'))
    #df.to_csv(datadir,index=False, header=True)

connection.commit()