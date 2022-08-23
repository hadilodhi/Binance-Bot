import pandas as pd
import os
from backtesting import Strategy
from backtesting import Backtest
import matplotlib.pyplot as plt
import seaborn as sns
from tabulate import tabulate

cwd = os.getcwd()
datadir = cwd + r"\Data.csv"

df = pd.read_csv(datadir, index_col='Time', parse_dates=True)

# Function to return the SMA
def SMA(values, n):
    return pd.Series(values).rolling(n).mean()
class SmaCross(Strategy):
    # Define the two MA lags as *class variables*
    ma_short = 15
    ma_medium = 35
    ma_long = 150
    df = df
    
    def init(self):
        # Precompute the two moving averages
        self.sma1 = self.I(SMA, self.df.Close.to_numpy(), self.ma_short)
        self.sma2 = self.I(SMA, self.df.Close.to_numpy(), self.ma_medium)
        self.sma3 = self.I(SMA, self.df.Close.to_numpy(), self.ma_long)
        self.buysignal = False
        self.sellsignal = False
        print("Ran configuration ", self.ma_short,",", self.ma_medium, ",", self.ma_long)
    
    def next(self):
        # If sma1 crosses above sma2 buy the asset
        if (self.sma1 > self.sma2) and (self.sma2 > self.sma3) and (self.buysignal == False):
            self.position.close()
            self.buy()
            self.buysignal = True
            self.sellsignal = False
        # Else, if sma1 crosses below sma2 sell the asset
        elif (self.sma1 < self.sma2) and (self.sma2 < self.sma3) and (self.sellsignal == False):
            self.position.close()
            self.sell()
            self.sellsignal = True
            self.buysignal = False

r"""

# reminder that we use this Backtest class
bt = Backtest(data=df, strategy=SmaCross, cash=100000, commission=.0001, margin=0.1)
# evaluate all possible combinations
stats, heatmap = bt.optimize(
    ma_short=range(5, 50, 5),
    ma_medium=range(30, 80, 5),
    ma_long=range(70, 200, 5),
    constraint=lambda p: p.ma_short < p.ma_medium and p.ma_medium < p.ma_long,
    maximize='Equity Final [$]',
    return_heatmap=True)
# check the top 10 returns
print(heatmap.sort_values(ascending=False).iloc[:10])

# group 
hm = heatmap.groupby(['ma_short', 'ma_medium', 'ma_long']).mean().unstack()


plt.figure(figsize=(12, 10))
sns.heatmap(hm[::-1], cmap='viridis')
plt.show()

r"""

# run the backtest
bt = Backtest(data=df, strategy=SmaCross, cash=1000000, commission=0, margin=1)
stats = bt.run()

print(stats)
print(tabulate(stats['_trades'], headers='keys', tablefmt='psql'))
#print(tabulate(df, headers='keys', tablefmt='psql'))