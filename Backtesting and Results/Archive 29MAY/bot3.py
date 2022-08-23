import pandas as pd
import os
from backtesting import Strategy
from backtesting import Backtest
import matplotlib.pyplot as plt
import seaborn as sns
from tabulate import tabulate
import talib

cwd = os.getcwd()
datadir = cwd + r"\Data.csv"

df = pd.read_csv(datadir)
df = df[["CloseTime", "Open", "High", "Low", "Close"]]
df["CloseTime"] = pd.to_datetime(df["CloseTime"], unit='ms')
df.rename(columns={"CloseTime": "Time"}, inplace=True)
df.set_index('Time', inplace= True)

class SmaCross(Strategy):

    period = 5
    df = df
    talib = talib
    current = 0

    def init(self):
        self.df['Aroon'] = (self.talib.AROONOSC(self.df['High'], self.df['Low'], self.period)) / 100
        self.df['pAroon'] = self.df['Aroon'].shift(1)
        self.df = self.df.iloc[self.period + 1:]
        print(tabulate(self.df, headers='keys', tablefmt='psql'))
        
        self.buy(size=0.8)
        

    def next(self):
        self.current = self.current + 1
        if self.current == 1:
            print(float(self.df['Aroon'].iloc[1]))
            #self.buy(size=self.df['Aroon'].iloc[self.current])
            return
            




r"""
# reminder that we use this Backtest class
bt = Backtest(data=df, strategy=SmaCross, cash=100000, commission=.0001)
# evaluate all possible combinations
stats, heatmap = bt.optimize(
    period=range(4, 10, 2),
    multiplier=range(2, 4, 1),
    ma_short=range(5, 50, 5),
    ma_long=range(5, 150, 5),
    constraint=lambda p: p.ma_short < p.ma_long,
    maximize='Equity Final [$]',
    return_heatmap=True)
# check the top 10 returns
print(heatmap.sort_values(ascending=False).iloc[:10])

# group 
hm = heatmap.groupby(['period', 'multiplier','ma_short', 'ma_long']).mean().unstack()


plt.figure(figsize=(12, 10))
sns.heatmap(hm[::-1], cmap='viridis')
plt.show()

r"""

# run the backtest
bt = Backtest(data=df, strategy=SmaCross, cash=1000000, commission=.0001)
stats = bt.run()
print(stats)
print(tabulate(stats['_trades'], headers='keys', tablefmt='psql'))
