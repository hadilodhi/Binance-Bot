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
    with open("error.txt", "a") as file_object:
        file_object.write("Error at " + currenttime + ": " + str(e) + "\n\n")
    push = pb.push_note('Error Occured',str(e))

def createorder(side, quantity, currenttime):
    global order
    try:
        order = client.futures_create_order(
                symbol='BTCUSDT',
                side=side,
                type='MARKET',
                quantity=quantity)
        return order
    except BinanceAPIException as e:
        errorpush(e,currenttime)
        print(e)
    except BinanceOrderException as e:
        errorpush(e,currenttime)
        print(e)

f = open('parameters.json')
parameters = json.load(f)

client = Client(config.API_KEY, config.API_SECRET)
info = client.futures_account()
print(info['totalMarginBalance'])
# for i in info['positions']:
#     if i['symbol'] == 'BTCUSDT':
#         leverage = i['leverage']
# balances = client.futures_account_balance()
# for balance in balances:
#     if balance['asset'] == 'USDT':
#         USDTbalance = balance['balance']
r"""
candles = client.futures_klines(symbol='BTCUSDT', interval=Client.KLINE_INTERVAL_30MINUTE,limit=300)
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
debug = False
firstbet = True

BTCprice = df.iloc[bar_offset,3]
quantity = (float(USDTbalance)/float(BTCprice))*quantitymodifier #*int(leverage)
quantity = quantity // 0.001 * 0.001
#quantity = 0.001
#print(quantity)

with open('lastorder.pkl', 'rb') as f:
    orderID, side, prevquantity = pickle.load(f)

print("Previous orderID =", orderID, "and side =", side)
with open("log.txt", "a") as file_object:
    file_object.write("Previous orderID = " + str(orderID) + " and side = " + str(side) + "\n")

if df.iloc[bar_offset, 4] >= df.iloc[bar_offset, 6] and df.iloc[bar_offset, 7] <= df.iloc[bar_offset, 8] and df.iloc[bar_offset,4] <= df.iloc[bar_offset,5] and df.iloc[bar_offset, 9] >= df.iloc[bar_offset, 10] and side == 'SELL':
    side = 'BUY'
    if debug == False:
        if firstbet == False:
            createorder(side,prevquantity, currenttime)
            time.sleep(1)
        createorder(side,quantity, currenttime)
        orderID = order['orderId']
    else:
        orderID = currenttime + ' Testing'
    prevquantity = quantity
    with open('lastorder.pkl', 'wb') as f:
        pickle.dump([orderID, side, prevquantity], f)
    print(currenttime, "Bought", quantity, "BTC for", BTCprice)
    print("orderID =", orderID, "and side =", side)
    with open("log.txt", "a") as file_object:
        file_object.write(currenttime + " Bought " + str(quantity) + " BTC for " + str(BTCprice) + "\n")
    with open("log.txt", "a") as file_object:
        file_object.write("orderID = " + str(orderID) + " and side = " + str(side) + "\n\n")
    if debug == False:
        push = pb.push_note('Bought BTC',str(quantity) + 'BTC for ' + str(BTCprice))
    else:
        push = pb.push_note('Bought BTC (debug)',str(quantity) + 'BTC for ' + str(BTCprice))

elif df.iloc[bar_offset, 4] <= df.iloc[bar_offset, 6] and df.iloc[bar_offset, 7] >= df.iloc[bar_offset, 8] and df.iloc[bar_offset,4] >= df.iloc[bar_offset,5] and df.iloc[bar_offset, 9] <= df.iloc[bar_offset, 10] and side == 'BUY':
    side = 'SELL'
    if debug == False:
        if firstbet == False:
            createorder(side,prevquantity, currenttime)
            time.sleep(1)
        createorder(side,quantity, currenttime)
        orderID = order['orderId']
    else:
        orderID = currenttime + ' Testing'
    prevquantity = quantity
    with open('lastorder.pkl', 'wb') as f:
        pickle.dump([orderID, side, prevquantity], f)
    print(currenttime, "Sold", quantity, "BTC for", BTCprice)
    print("orderID =", orderID, "and side =", side)
    with open("log.txt", "a") as file_object:
        file_object.write(currenttime + " Sold " + str(quantity) + " BTC for " + str(BTCprice) + "\n")
    with open("log.txt", "a") as file_object:
        file_object.write("orderID = " + str(orderID) + " and side = " + str(side) + "\n\n")
    if debug == False:
        push = pb.push_note('Sold BTC',str(quantity) + 'BTC for ' + str(BTCprice))
    else:
        push = pb.push_note('Sold BTC (debug)',str(quantity) + 'BTC for ' + str(BTCprice))

else:
    print(currenttime, 'nothing to do')
    with open("log.txt", "a") as file_object:
        file_object.write(currenttime + " nothing to do \n\n")
r"""