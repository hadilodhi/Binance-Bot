from binance.client import Client
from binance.enums import *
from binance.exceptions import BinanceAPIException, BinanceOrderException
import config
from pandas import DataFrame
import pandas as pd
from datetime import datetime
from tabulate import tabulate
import json
import pickle
from pushbullet import Pushbullet
import pandas_ta as ta
import time

pb = Pushbullet(config.pbAPI)

def errorpush(e,currenttime):
    push = pb.push_note('Error Occured',str(e))
    print(e)

def normalpush(BTCprice, side, quantity, currenttime):
    print(currenttime, side, quantity, "BTC for", BTCprice)
    if debug == False:
        push = pb.push_note(str(side),str(quantity) + 'BTC for ' + str(BTCprice))
    else:
        push = pb.push_note(str(side) + " (debug)",str(quantity) + 'BTC for ' + str(BTCprice))

def createorder(side, quantity, currenttime):
    try:
        order = client.futures_create_order(
                symbol='BTCUSDT',
                side=side,
                type='MARKET',
                quantity=quantity)
        return order
    except BinanceAPIException as e:
        errorpush(e,currenttime)
    except BinanceOrderException as e:
        errorpush(e,currenttime)

f = open('parameters.json')
parameters = json.load(f)

client = Client(config.API_KEY, config.API_SECRET)
trades = client.futures_account_trades()
side = trades[-1]['side']
prevquantity = trades[-1]['qty']
orderID = trades[-1]['orderId']

info = client.futures_account()
for i in info['positions']:
    if i['symbol'] == 'BTCUSDT':
        leverage = i['leverage']
balances = client.futures_account_balance()
for balance in balances:
    if balance['asset'] == 'USDT':
        USDTbalance = balance['balance']

candles = client.futures_klines(symbol='BTCUSDT', interval=Client.KLINE_INTERVAL_30MINUTE,limit=500)
df = DataFrame(candles, columns=["time", "open", "high", "low", "close","volume", "closeTime", "QAV", "NofT", "TBBAV", "TBQAV", "Ignore"])
df = df.drop(["volume","closeTime", "QAV", "NofT", "TBBAV", "TBQAV", "Ignore"], 1)
df["time"] = pd.to_datetime(df["time"], unit='ms')
df.set_index('time', inplace=True)

ma_short = 5
ma_long = 10

macdfast = parameters['macdfast']
macdslow = parameters['macdslow']
macdsignal = parameters['macdsignal']

currenttime = datetime.now()
currenttime = currenttime.strftime("%Y-%m-%d %H:%M:%S")
#print(currenttime)
df["close"] = pd.to_numeric(df["close"])
df.ta.macd(fast=macdfast, slow=macdslow, signal=macdsignal, append=True) # fast=12, slow=26, signal=9
df['previousfast'] = df.iloc[:,4].shift(1)
df['previousslow'] = df.iloc[:,6].shift(1)
df['MA_' + str(ma_short)] = ta.sma(df["close"], length=ma_short)
df['MA_' + str(ma_long)] = ta.sma(df["close"], length=ma_long)
#print(tabulate(df.tail(10), headers='keys', tablefmt='psql'))

bar_offset = -2
quantitymodifier = 1
debug = True
firstbet = True
#side = 'SELL'

BTCprice = df.iloc[bar_offset,3]
quantity = (float(USDTbalance)/float(BTCprice))*quantitymodifier*int(leverage)
quantity = quantity // 0.001 * 0.001
#quantity = 0.001
#print(quantity)

print("Previous orderID =", orderID, "and side =", side)

if df.iloc[bar_offset, 4] >= df.iloc[bar_offset, 6] and df.iloc[bar_offset, 7] <= df.iloc[bar_offset, 8] and df.iloc[bar_offset,4] <= df.iloc[bar_offset,5] and df.iloc[bar_offset, 9] >= df.iloc[bar_offset, 10] and side == 'SELL':
    side = 'BUY'
    if debug == False:
        if firstbet == False:
            createorder(side,prevquantity, currenttime)
            time.sleep(1)
        createorder(side,quantity, currenttime)
    normalpush(BTCprice, side, quantity, currenttime)

elif df.iloc[bar_offset, 4] <= df.iloc[bar_offset, 6] and df.iloc[bar_offset, 7] >= df.iloc[bar_offset, 8] and df.iloc[bar_offset,4] >= df.iloc[bar_offset,5] and df.iloc[bar_offset, 9] <= df.iloc[bar_offset, 10] and side == 'BUY':
    side = 'SELL'
    if debug == False:
        if firstbet == False:
            createorder(side,prevquantity, currenttime)
            time.sleep(1)
        createorder(side,quantity, currenttime)
    normalpush(BTCprice, side, quantity, currenttime)

else:
    print(currenttime, 'nothing to do')