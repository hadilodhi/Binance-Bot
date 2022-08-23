from pandas import DataFrame
import multiprocessing as mp
import pandas as pd
import os
import numpy as np
from tabulate import tabulate

def initdf():
    global df
    global df3
    global SL
    cwd = os.getcwd()
    datadir = cwd + r"\Data.csv"

    df = pd.read_csv(datadir, index_col='Time', parse_dates=True)
    Increment = 5
    R1 = [5,50]
    R2 = [30,80]
    R3 = [70,200]
    R4 = [R1,R2,R3]
    SL = 1.50
    LT = []
    for x in range(R4[0][0], R4[0][1]+1, Increment):
        for y in range(R4[1][0], R4[1][1]+1, Increment):
            if x < y:
                for z in range(R4[2][0], R4[2][1]+1, Increment):
                    if x < y < z:
                        LT.append([x,y,z])
    df3 = DataFrame (LT,columns=['MA1','MA2','MA3'])

def CalcPerc (i,df,ma_short,ma_medium,ma_long,stoploss):
    df['MA_' + str(ma_short)] = pd.Series(df['Close']).rolling(ma_short).mean()
    df['MA_' + str(ma_medium)] = pd.Series(df['Close']).rolling(ma_medium).mean()
    df['MA_' + str(ma_long)] = pd.Series(df['Close']).rolling(ma_long).mean()
    df.loc[(df.iloc[:, 4] > df.iloc[:, 5]) & (df.iloc[:, 5] > df.iloc[:, 6]),['buy']] = 1
    df.loc[(df.iloc[:, 4] < df.iloc[:, 5]) & (df.iloc[:, 5] < df.iloc[:, 6]),['buy']] = 0
    df = df.ffill()
    df['duplicate'] = df['buy'].shift(1)
    df['buy'] = df.apply(lambda x: np.nan if x['buy'] == x['duplicate'] \
                            else x['buy'], axis=1)
    df['percentage'] = df['buy']
    df.loc[(df['percentage'] == 0),['percentage']] = 1
    df['ipercentage'] = df['percentage']
    df['duplicate'] = df['buy']
    df['duplicate'] = df['duplicate'].ffill()
    df.loc[(df['percentage'] == 1),['duplicate']] = np.nan
    df.loc[(df['ipercentage'] == 1),['ipercentage']] = df['Close']
    df['ipercentage'] = df['ipercentage'].ffill()
    df.loc[(df['percentage'] == 1),['ipercentage']] = np.nan
    df['ipercentage'] = df.apply(lambda x: round(((x['Close'] - x['ipercentage']) / x['ipercentage']) * 100, 2) if x['duplicate'] == 1 \
                            else(-round(((x['Close'] - x['ipercentage']) / x['ipercentage']) * 100, 2) if x['duplicate'] == 0 else np.nan), axis=1)
    df['difference'] = df['ipercentage'].shift(1)
    df['difference'] = df.apply(lambda x: x['ipercentage'] - x['difference'] if pd.notnull(x['ipercentage']) and pd.notnull(x['difference']) \
                            else np.nan, axis = 1)
    sl = 0
    df['SL'] = np.nan
    for x in range(0,len(df)):
        if pd.notnull(df['difference'].iloc[x]):
            sl = sl + df['difference'].iloc[x]
            if sl >= 0:
                sl = 0
            df['SL'].iloc[x] = sl
        else:
            sl = 0
    df=df.drop(['duplicate', 'ipercentage', 'difference'], axis = 1)
    df.loc[(df['SL'] < -stoploss),['buy']] = 2
    df['percentage'] = df['buy']
    df.loc[(df['percentage'] == 0),['percentage']] = 1
    df['sell'] = df['buy']
    df.loc[(df['buy'] == 1),['buy']] = df['Close']
    df.loc[(df['sell'] == 0),['sell']] = df['Close']
    df.loc[(df['percentage'] == 1),['percentage']] = df['Close']
    df['location'] = df['percentage'].shift(-1)
    df = df.ffill()
    df = df.replace(2,np.nan)
    df.loc[(df['sell'] == 1),['sell']] = 0
    df['percentage'] = df.apply(lambda x: x['percentage'] if x['percentage'] != x['location'] \
                            else np.nan, axis=1)
    df['location'] = df['location'].shift(2)
    df['percentage'] = df['percentage'].shift(1)
    df['location'] = df.apply(lambda x: np.nan if pd.isnull(x['percentage']) \
                            else x['location'], axis=1)
    df['percentage'] = df.apply(lambda x: x['Close'] if pd.notnull(x['location']) \
                            else np.nan, axis=1)
    if df["buy"].iloc[-1] == 0 or df["sell"].iloc[-1] == 0:
        df["location"].iloc[-1] = df["Close"].iloc[-1]
    if df["buy"].iloc[-1] == 0:
        df["percentage"].iloc[-1] = df["sell"].iloc[-1]
    else:
        df["percentage"].iloc[-1] = df["buy"].iloc[-1]
    df['percentage'] = df.apply(lambda x: round(((x['percentage'] - x['location']) / x['location']) * 100, 2) if pd.notnull(x['location']) \
                            else np.nan, axis=1)
    if df["buy"].iloc[-1] == 0:
        df["location"].iloc[-1] = df["sell"].iloc[-1]
    else:
        df["location"].iloc[-1] = df["buy"].iloc[-1]
    df['buy1'] = df['buy'].shift(1)
    df['sell1'] = df['sell'].shift(1)
    df['percentage'] = df.apply(lambda x: - x['percentage'] if x['sell1'] != 0 and x['buy1'] == 0 and pd.notnull(x['location'])\
                            else x['percentage'], axis=1)
    df["percentage"].iloc[-1] = -df["percentage"].iloc[-1]
    df=df.drop(['buy1', 'sell1'], axis = 1)
    df2 = df[['percentage']]
    df2 = df2.dropna()
    df['percentage'] = df.apply(lambda x: str(x['percentage']) + ' %' if pd.notnull(x['percentage'])\
                            else x['percentage'], axis=1)
    df.replace(0, np.nan, inplace=True)
    df2["return"] = df2["percentage"].cumsum()
    df2["drawdown"] = df2["return"] - df2["return"].cummax()
    profit = round(df2['return'].max(), 2)
    drawdown = round(df2["drawdown"].min(), 2)
    return(i,ma_short,ma_medium,ma_long,profit,drawdown,stoploss)

def get_result(result):
    print("Result",result)
    global results
    results.append(result)

if __name__ == '__main__':
    results = []
    initdf()
    pool = mp.Pool(mp.cpu_count())
    for i in range(0, len(df3.index)):
        pool.apply_async(CalcPerc, args=(i,df, df3['MA1'].iloc[i], df3['MA2'].iloc[i], df3['MA3'].iloc[i],SL), callback=get_result)
    pool.close()
    pool.join()
    df4 = DataFrame (results,columns=['Index','MA1','MA2','MA3','Profit','Drawdown','Stoploss'])
    df4 = df4.sort_values(['Profit'], ascending=[0])
    df4.drop(['Index'], inplace=True, axis=1)
    df4 = df4.head(10)
    cwd = os.getcwd()
    datadir = cwd + r"\Backtesting.csv"
    df4.to_csv(datadir,index=False, header=True)
    print(tabulate(df4, headers='keys', tablefmt='psql'))
    df4.drop(['Profit','Drawdown'], inplace=True, axis=1)
    df4 = df4.reset_index()
    with open('MAs.json', 'w') as f:
        f.write(df4.head(1).to_json())