from binance.client import Client
from binance.enums import *
from binance.exceptions import BinanceAPIException, BinanceOrderException
from pandas import DataFrame
import pandas as pd
from datetime import datetime
from tabulate import tabulate
from pushbullet import Pushbullet
import pandas_ta as ta
import time
import pause
from datetime import datetime, timedelta
import os,time
from configvar import *

#pb = Pushbullet(os.environ['pbAPI'])
client = Client(authlist['binance'][0]['API'], authlist['binance'][0]['SEC'])

def errorpush(e,currenttime):
    pb = Pushbullet(authlist['pushbullet'][0]['API'])
    push = pb.push_note('Error Occured',str(e))
    print(e)

def normalpush(debug, BTCprice, side, quantity, currenttime):
    print(currenttime, side, quantity, "BTC for", BTCprice)
    for apis in authlist['pushbullet']:
        if apis['API'] != "":
            pb = Pushbullet(apis['API'])
            if debug == 'False':
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

def main(debug):
    trades = client.futures_account_trades()
    side = trades[-1]['side']
    prevquantity = trades[-1]['qty']
    orderID = trades[-1]['orderId']

    info = client.futures_account()
    for i in info['positions']:
        if i['symbol'] == 'BTCUSDT':
            leverage = i['leverage']
    # balances = client.futures_account_balance()
    # for balance in balances:
    #     if balance['asset'] == 'USDT':
    #         USDTbalance = balance['balance']
    USDTbalance = info['totalMarginBalance']

    candles = client.futures_klines(symbol='BTCUSDT', interval=Client.KLINE_INTERVAL_30MINUTE,limit=500)
    df = DataFrame(candles, columns=["time", "open", "high", "low", "close","volume", "closeTime", "QAV", "NofT", "TBBAV", "TBQAV", "Ignore"])
    df = df.drop(["volume","closeTime", "QAV", "NofT", "TBBAV", "TBQAV", "Ignore"], 1)
    df["time"] = pd.to_datetime(df["time"], unit='ms')
    df.set_index('time', inplace=True)

    ma_short = 5
    ma_long = 10

    macdfast = int(os.environ['macdfast'])
    macdslow = int(os.environ['macdslow'])
    macdsignal = int(os.environ['macdsignal'])

    currenttime = datetime.now()
    currenttime = currenttime.strftime("%Y-%m-%d %H:%M:%S")
    #print(currenttime)
    df["close"] = pd.to_numeric(df["close"])
    df.ta.macd(fast=macdfast, slow=macdslow, signal=macdsignal, append=True) # fast=12, slow=26, signal=9
    df['previousfast'] = df.iloc[:,4].shift(1)
    df['previousslow'] = df.iloc[:,6].shift(1)
    df['MA_' + str(ma_short)] = ta.sma(df["close"], length=ma_short)
    df['MA_' + str(ma_long)] = ta.sma(df["close"], length=ma_long)

    bar_offset = -int(os.environ['bar_offset'])
    quantitymodifier = float(os.environ['size'])
    firstbet = os.environ['firstbet']

    if debug == 'True':
        side = os.environ['debugside']
    if debug == 'True' or os.environ['printvals'] == 'True':
        print(tabulate(df.tail(-bar_offset).head(1).drop(["open", "high", "low", "close"], 1), headers='keys', tablefmt='psql'))

    BTCprice = df.iloc[bar_offset,3]
    quantity = (float(USDTbalance)/float(BTCprice))*quantitymodifier*int(leverage)
    quantity = quantity // 0.001 * 0.001
    #quantity = 0.001
    #print(quantity)

    print("Previous orderID =", orderID, "and side =", side)

    if df.iloc[bar_offset, 4] >= df.iloc[bar_offset, 6] and df.iloc[bar_offset, 7] <= df.iloc[bar_offset, 8] and df.iloc[bar_offset,4] <= df.iloc[bar_offset,5] and df.iloc[bar_offset, 9] >= df.iloc[bar_offset, 10] and side == 'SELL':
        side = 'BUY'
        if debug == 'False':
            if firstbet == 'False':
                createorder(side,prevquantity, currenttime)
                time.sleep(1)
            createorder(side,quantity, currenttime)
        normalpush(debug, BTCprice, side, quantity, currenttime)

    elif df.iloc[bar_offset, 4] <= df.iloc[bar_offset, 6] and df.iloc[bar_offset, 7] >= df.iloc[bar_offset, 8] and df.iloc[bar_offset,4] >= df.iloc[bar_offset,5] and df.iloc[bar_offset, 9] <= df.iloc[bar_offset, 10] and side == 'BUY':
        side = 'SELL'
        if debug == 'False':
            if firstbet == 'False':
                createorder(side,prevquantity, currenttime)
                time.sleep(1)
            createorder(side,quantity, currenttime)
        normalpush(debug, BTCprice, side, quantity, currenttime)

    else:
        print(currenttime, 'nothing to do')

def ceil_dt(dt, delta):
    return dt + (datetime.min - dt) % delta

debug = os.environ['debug']
if debug == 'True':
    main(debug)
while 1:
    now = datetime.now()
    stoptill = ceil_dt(now, timedelta(minutes=30))
    # stoptill = ceil_dt(now, timedelta(seconds=30))
    # stoptill = (now + relativedelta(seconds=10)).strftime("%Y-%m-%d %H:%M:%S")
    # stoptill = datetime.strptime(stoptill, "%Y-%m-%d %H:%M:%S")
    print('Waiting till',stoptill)
    pause.until(stoptill)
    time.sleep(5)
    main(debug)