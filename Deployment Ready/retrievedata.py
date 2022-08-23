from binance.client import Client
import config
from pandas import DataFrame
import pandas as pd
import os
from datetime import date, datetime
from dateutil.relativedelta import relativedelta
cwd = os.getcwd()
datadir = cwd + r"\Data.csv"

client = Client(config.API_KEY, config.API_SECRET)
startdate = (datetime.today() - relativedelta(months=6)).strftime("%d %b, %Y")
#enddate = (date.today() - relativedelta(days=15)).strftime("%d %b, %Y")
#enddate = datetime.today().strftime("%d %b, %Y")

candles = client.futures_historical_klines("BTCUSDT", Client.KLINE_INTERVAL_30MINUTE, startdate)
#candles = client.futures_klines(symbol='BTCUSDT', interval=Client.KLINE_INTERVAL_30MINUTE,limit=300)
df = DataFrame(candles, columns=["time", "open", "high", "low", "close","volume", "closeTime", "QAV", "NofT", "TBBAV", "TBQAV", "Ignore"])
df = df.drop(["volume","closeTime", "QAV", "NofT", "TBBAV", "TBQAV", "Ignore"], 1)
df["time"] = pd.to_datetime(df["time"], unit='ms')
df.to_csv(datadir,index=False, header=True)
print('Retrieved Data Successfully')
