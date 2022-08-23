import pandas as pd
import os
from backtesting import Strategy
from backtesting import Backtest
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



def SMA(values, n):
    return pd.Series(values).rolling(n).mean()

class SmaCross(Strategy):
    # Define the two MA lags as *class variables*
    ma1 = 15
    ma2 = 30
    ma3 = 185
    df = df
    stoploss = 0.02
    
    def init(self):
        # Precompute the three moving averages
        self.sma1 = self.I(SMA, self.df.Close.to_numpy(), self.ma1)
        self.sma2 = self.I(SMA, self.df.Close.to_numpy(), self.ma2)
        self.sma3 = self.I(SMA, self.df.Close.to_numpy(), self.ma3)
        self.buysignal = False
        self.sellsignal = False
        self.price = 0
        self.percentage = 0.0
        self.currentpercentage = 0.0
        self.difference = 0.0
        self.i = 0
        print("Ran configuration ", self.ma1,",", self.ma2,",", self.ma3)

    def next(self):
        self.i = self.i + 1

        if(self.buysignal == True):
            self.currentpercentage = (self.df["Close"].iloc[self.i] - self.price) / self.price
        elif(self.sellsignal == True):
            self.currentpercentage = -(self.df["Close"].iloc[self.i] - self.price) / self.price

        self.difference = self.difference + (self.currentpercentage - self.percentage)
        if(self.difference > 0.0):
            self.difference = 0.0
        self.percentage = self.currentpercentage
        
        # If sma1 crosses above sma2 buy the asset
        if (self.sma1 > self.sma2) and (self.sma2 > self.sma3) and (self.buysignal == False):
            self.position.close()
            self.buy()
            self.buysignal = True
            self.sellsignal = False
            self.price = self.df["Close"].iloc[self.i]
            self.percentage = 0.0
            self.currentpercentage = 0.0
            self.difference = 0.0

        # Else, if sma1 crosses below sma2 sell the asset
        elif (self.sma1 < self.sma2) and (self.sma2 < self.sma3) and (self.sellsignal == False):
            self.position.close()
            self.sell()
            self.sellsignal = True
            self.buysignal = False
            self.price = self.df["Close"].iloc[self.i]
            self.percentage = 0.0
            self.currentpercentage = 0.0
            self.difference = 0.0

        if(self.difference < -self.stoploss):
            self.position.close()
            self.sellsignal = False
            self.buysignal = False
            self.price = 0
            self.percentage = 0.0
            self.currentpercentage = 0.0
            self.difference = 0.0

r"""

# reminder that we use this Backtest class
bt = Backtest(data=df, strategy=SmaCross, cash=100000, commission=.0001)
# evaluate all possible combinations
stats, heatmap = bt.optimize(
    ma1=range(5, 50, 5),
    ma2=range(30, 80, 5),
    ma3=range(70, 200, 5),
    constraint=lambda p: p.ma1 < p.ma2 and p.ma2 < p.ma3,
    maximize='Equity Final [$]',
    return_heatmap=True)
# check the top 10 returns
print(heatmap.sort_values(ascending=False).iloc[:10])

# group 
hm = heatmap.groupby(['ma1', 'ma2', 'ma3']).mean().unstack()


plt.figure(figsize=(12, 10))
sns.heatmap(hm[::-1], cmap='viridis')
plt.show()
"""

# run the backtest
bt = Backtest(data=df, strategy=SmaCross, cash=1000000, commission=.0001)
stats = bt.run()

#print(tabulate(stats['_trades'], headers='keys', tablefmt='psql'))
print(stats)
