import pandas as pd
import os
from backtesting import Strategy
from backtesting import Backtest
from backtesting.lib import crossover
import matplotlib.pyplot as plt
import seaborn as sns
from tabulate import tabulate

cwd = os.getcwd()
datadir = cwd + r"\Data.csv"

df = pd.read_csv(datadir)
df = df[["CloseTime", "Open", "High", "Low", "Close"]]
df["CloseTime"] = pd.to_datetime(df["CloseTime"], unit='ms')
df.rename(columns={"CloseTime": "Time"}, inplace=True)
df.set_index('Time', inplace= True)

# Function to return the SMA
def SMA(values, n):
    return pd.Series(values).rolling(n).mean()
class SmaCross(Strategy):
    # Define the two MA lags as *class variables*
    ma_short = 5
    ma_long = 145
    df = df
    
    def init(self):
        # Precompute the two moving averages
        self.sma1 = self.I(SMA, self.df.Close.to_numpy(), self.ma_short)
        self.sma2 = self.I(SMA, self.df.Close.to_numpy(), self.ma_long)
        print("Ran configuration ", self.ma_short,",", self.ma_long)
    
    def next(self):
        # If sma1 crosses above sma2 buy the asset
        if crossover(self.sma1, self.sma2):
            self.position.close()
            self.buy()
        # Else, if sma1 crosses below sma2 sell the asset
        elif crossover(self.sma2, self.sma1):
            self.position.close()
            self.sell()

r"""

# reminder that we use this Backtest class
bt = Backtest(data=df, strategy=SmaCross, cash=100000, commission=.0001)
# evaluate all possible combinations
stats, heatmap = bt.optimize(
    ma_short=range(5, 200, 5),
    ma_long=range(5, 200, 5),
    constraint=lambda p: p.ma_short < p.ma_long,
    maximize='Equity Final [$]',
    return_heatmap=True)
# check the top 10 returns
print(heatmap.sort_values(ascending=False).iloc[:10])

# group 
hm = heatmap.groupby(['ma_short', 'ma_long']).mean().unstack()


plt.figure(figsize=(12, 10))
sns.heatmap(hm[::-1], cmap='viridis')
plt.show()

r"""

# run the backtest
bt = Backtest(data=df, strategy=SmaCross, cash=1000000, commission=.0001)
stats = bt.run()
print(stats)
print(tabulate(stats['_trades'], headers='keys', tablefmt='psql'))