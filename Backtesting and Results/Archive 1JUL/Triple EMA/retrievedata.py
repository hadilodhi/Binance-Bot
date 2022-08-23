from binance.client import Client
import config
from pandas import DataFrame
import pandas as pd
import os
from datetime import date
from dateutil.relativedelta import relativedelta
cwd = os.getcwd()
datadir = cwd + r"\Data.csv"

client = Client(config.API_KEY, config.API_SECRET)
startdate = (date.today() - relativedelta(days=14)).strftime("%d %b, %Y")
enddate = date.today().strftime("%d %b, %Y")

candles = client.get_historical_klines("BTCUSDT", Client.KLINE_INTERVAL_30MINUTE, startdate, enddate)
#candles = client.get_klines(symbol='BTCUSDT', interval=Client.KLINE_INTERVAL_30MINUTE,limit=1000)
df = DataFrame(candles, columns=["Time", "Open", "High", "Low", "Close","Volume", "CloseTime", "QAV", "NofT", "TBBAV", "TBQAV", "Ignore"])
df = df.drop(["Volume","CloseTime", "QAV", "NofT", "TBBAV", "TBQAV", "Ignore"], 1)
df["Time"] = pd.to_datetime(df["Time"], unit='ms')
df.to_csv(datadir,index=False, header=True)
