from pandas import DataFrame
import multiprocessing as mp
import pandas as pd
import os
import numpy as np
from tabulate import tabulate
import pandas_ta as ta

def initdf():
    global df
    global df3
    cwd = os.getcwd()
    datadir = cwd + r"\Data.csv"

    df = pd.read_csv(datadir, index_col='time', parse_dates=True)
    Increment = 5
    R1 = [5,200]
    R2 = [5,200]
    R4 = [R1,R2]
    LT = []
    for x in range(R4[0][0], R4[0][1]+1, Increment):
        for y in range(R4[1][0], R4[1][1]+1, Increment):
            if x < y:
                LT.append([x,y])
    df3 = DataFrame (LT,columns=['MA1','MA2'])

def CalcPerc (i,df,ma_short,ma_medium):
    df['MA_' + str(ma_short)] = ta.sma(df["close"], length=ma_short)
    df['MA_' + str(ma_medium)] = ta.sma(df["close"], length=ma_medium)
    df.loc[df.iloc[:, 4] > df.iloc[:, 5],['buy']] = 1
    df.loc[df.iloc[:, 4] < df.iloc[:, 5],['buy']] = 0
    df = df.ffill()
    df['duplicate'] = df['buy'].shift(1)
    df['buy'] = df.apply(lambda x: np.nan if x['buy'] == x['duplicate'] \
                            else x['buy'], axis=1)
    df = df.drop('duplicate', axis=1)
    df['percentage'] = df['buy']
    df.loc[(df['percentage'] == 0),['percentage']] = 1
    df['sell'] = df['buy']
    df.loc[(df['buy'] == 1),['buy']] = df['close']
    df.loc[(df['sell'] == 0),['sell']] = df['close']
    df.loc[(df['percentage'] == 1),['percentage']] = df['close']
    df['location'] = df['percentage'].shift(1)
    df = df.ffill()
    df.loc[(df['sell'] == 1),['sell']] = 0
    df['percentage'] = df.apply(lambda x: x['percentage'] if x['percentage'] != x['location'] \
                            else np.nan, axis=1)
    df['location'] = df.apply(lambda x: np.nan if pd.isnull(x['percentage']) \
                            else x['location'], axis=1)
    df["location"].iloc[-1] = df["close"].iloc[-1]
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
    df['percentage'] = df.apply(lambda x: - x['percentage'] if x['sell'] == 0 and x['buy'] != 0 and pd.notnull(x['location'])\
                            else x['percentage'], axis=1)
    df2 = df[['percentage']]
    df2 = df2.dropna()
    df['percentage'] = df.apply(lambda x: str(x['percentage']) + ' %' if pd.notnull(x['percentage'])\
                            else x['percentage'], axis=1)
    df.replace(0, np.nan, inplace=True)
    df2["return"] = df2["percentage"].cumsum()
    df2["drawdown"] = df2["return"] - df2["return"].cummax()
    profit = round(df2['return'].max(), 2)
    drawdown = round(df2["drawdown"].min(), 2)
    return(i,ma_short,ma_medium,profit,drawdown)

def get_result(result):
    print("Result",result)
    global results
    results.append(result)

if __name__ == '__main__':
    results = []
    initdf()
    pool = mp.Pool(mp.cpu_count())
    for i in range(0, len(df3.index)):
        pool.apply_async(CalcPerc, args=(i,df, df3['MA1'].iloc[i], df3['MA2'].iloc[i]), callback=get_result)
    pool.close()
    pool.join()
    df4 = DataFrame (results,columns=['Index','MA1','MA2','Profit','Drawdown'])
    df4['adjusted profit'] = df4['Profit'] + df4['Drawdown']
    df4 = df4.sort_values(['adjusted profit'], ascending=[0])
    df4.drop(['Index','adjusted profit'], inplace=True, axis=1)
    df4 = df4.head(10)
    # cwd = os.getcwd()
    # datadir = cwd + r"\Backtesting.csv"
    # df4.to_csv(datadir,index=False, header=True)
    #print(tabulate(df4, headers='keys', tablefmt='psql'))
    df4.drop(['Profit','Drawdown'], inplace=True, axis=1)
    df4 = df4.reset_index()
    with open('MAs.json', 'w') as f:
        f.write(df4.head(1).to_json())
