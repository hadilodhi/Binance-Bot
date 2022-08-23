import pandas as pd
import os
from tabulate import tabulate
import numpy as np
import plotly.io as pio
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import plotly
import json
import pandas_ta as ta

pio.templates.default = "plotly_dark"

cwd = os.getcwd()
datadir = cwd + r"\Data.csv"
df = pd.read_csv(datadir, index_col='time', parse_dates=True)

f = open('parameters.json')
parameters = json.load(f)

ma_short = 5
ma_long = 10

macdfast = parameters['macdfast']['0']
macdslow = parameters['macdslow']['0']
macdsignal = parameters['macdsignal']['0']

df.ta.macd(fast=macdfast, slow=macdslow, signal=macdsignal, append=True) # fast=12, slow=26, signal=9
df['previousfast'] = df.iloc[:,4].shift(1)
df['previousslow'] = df.iloc[:,6].shift(1)
df['MA_' + str(ma_short)] = ta.sma(df["close"], length=ma_short)
df['MA_' + str(ma_long)] = ta.sma(df["close"], length=ma_long)
df.loc[(df.iloc[:, 4] >= df.iloc[:, 6]) & (df.iloc[:, 7] <= df.iloc[:, 8]) & (df.iloc[:,4] <= df.iloc[:,5]) & (df.iloc[:, 9] >= df.iloc[:, 10]),['buy']] = 1
df.loc[(df.iloc[:, 4] <= df.iloc[:, 6]) & (df.iloc[:, 7] >= df.iloc[:, 8]) & (df.iloc[:,4] >= df.iloc[:,5]) & (df.iloc[:, 9] <= df.iloc[:, 10]),['buy']] = 0
df = df.rename(columns={df.columns[4]: 'RSI',df.columns[4]: 'MACD Fast', df.columns[5]: 'MACD Signal', df.columns[6]: 'MACD Slow'})
df = df.drop(['previousfast', 'previousslow'], axis=1)

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

print("MA Config    ", ma_short,",", ma_long)
print("MACD Config  ", macdfast,",", macdslow,",", macdsignal)
print("Profit       ", round(df2['return'].max(), 2), "%")
print("Hold Return ", round((df.close[-1] - df.close[0]) / df.close[0] * 100, 2), "%")
print("Drawdown    ", round(df2["drawdown"].min(), 2), "%")
print("Win Rate     ", round(len(df2.loc[df2.percentage > 0]) / len(df2.index) * 100, 2), "%")
print("Exposure     ", round((df['buy'].count() + df['sell'].count()) / len(df.index) * 100, 2), "%")
print("Duration     ", (df.index[-1] - df.index[0]).days, "days")
print("No of Trades ", len(df2.index))
#print(tabulate(df.head(0), headers='keys', tablefmt='psql'))
#print(tabulate(df2, headers='keys', tablefmt='psql'))

layout = dict(
    title='Bitcoin MA+MACD Strategy',
    title_x=0.5,
    legend_title="Plots",
    margin=dict(l=20, r=100 ,t=60, b=10),
    paper_bgcolor='rgba(20,24,35,1)',
    plot_bgcolor='rgba(20,24,35,1)')
fig = make_subplots(rows=2,cols=1,shared_xaxes=True,vertical_spacing = 0,row_heights=[0.8, 0.2])
fig.add_trace(
    go.Ohlc(x=df.index,
    open=df['open'],
    high=df['high'],
    low=df['low'],
    close=df['close'],
    name="OHLC"),1,1)
fig.add_trace(
    go.Scatter(x=df.index,
    y=df.iloc[:, 7],
    line=dict(color='orange'),
    name=str('MA Fast')),1,1)
fig.add_trace(
    go.Scatter(x=df.index,
    y=df.iloc[:, 8],
    line=dict(color='blue'),
    name=str('MA Slow')),1,1)
fig.add_trace(
    go.Scatter(x=df.index,
    y=df['buy'],
    line=dict(color='green'),
    name='Buy'),1,1)
fig.add_trace(
    go.Scatter(x=df.index,
    y=df['sell'],
    line=dict(color='red'),
    name='Sell'),1,1)
fig.add_trace(
    go.Scatter(x=df.index,
    y=df.iloc[:, 5],
    line=dict(color='rgba(255,255,0,0.5)'),
    fill='tozeroy',
    name=str(df.columns[5])),2,1)
fig.add_trace(
    go.Scatter(x=df.index,
    y=df.iloc[:, 4],
    line=dict(color='orange'),
    name=str(df.columns[4])),2,1)
fig.add_trace(
    go.Scatter(x=df.index,
    y=df.iloc[:, 6],
    line=dict(color='blue'),
    name=str(df.columns[6])),2,1)
fig.add_trace(
    go.Scatter(x=df.index,
    y=df['location'],
    mode="markers+text",
    name="Percentages",
    text=df['percentage'],
    textposition="middle right"),1,1)
fig.add_annotation(text=
                "Profit             " + str(round(df2['return'].max(), 2)) + " %" + '<br>' +
                "Hold Return  " + str(round((df.close[-1] - df.close[0]) / df.close[0] * 100, 2)) + " %" + '<br>' + 
                "Drawdown    " + str(round(df2["drawdown"].min(), 2)) + " %" + '<br>' +
                "Win Rate       " + str(round(len(df2.loc[df2.percentage > 0]) / len(df2.index) * 100, 2)) + " %" + '<br>' +
                "Exposure       " + str(round((df['buy'].count() + df['sell'].count()) / len(df.index) * 100, 2)) + " %" + '<br>' + 
                "Duration        " + str((df.index[-1] - df.index[0]).days) + ' days<br>' + 
                "No of Trades  " + str(len(df2.index)),
                align='left',
                showarrow=False,
                xref='paper',
                yref='paper',
                x=1,
                y=1,
                bordercolor='rgba(39,43,54,1)',
                bgcolor='rgba(39,43,54,1)',
                borderwidth=2)
fig.add_annotation(text=
                "MA " + str(ma_short) + "," + str(ma_long),
                align='left',
                showarrow=False,
                xref='paper',
                yref='paper',
                x=0,
                y=1,
                bordercolor='rgba(39,43,54,1)',
                bgcolor='rgba(39,43,54,1)',
                borderwidth=2)
fig.add_annotation(text=
                "MACD " + str(macdfast) + "," + str(macdslow) + "," + str(macdsignal),
                align='left',
                showarrow=False,
                xref='paper',
                yref='paper',
                x=0,
                y=0.16,
                bordercolor='rgba(39,43,54,1)',
                bgcolor='rgba(39,43,54,1)',
                borderwidth=2)
fig.update_traces(xaxis="x2")
fig.update_layout(layout)
fig.update_xaxes(rangeslider=dict(visible = False))
fig.update_yaxes(autorange = True,fixedrange = False)
fig.update_xaxes(showline=True, linewidth=1, linecolor='rgba(39,43,54,1)', mirror=True,showspikes=True, spikemode='across', spikesnap='cursor',spikethickness=1,spikecolor='rgba(256,256,256,0.5)')
fig.update_yaxes(showline=True, linewidth=1, linecolor='rgba(39,43,54,1)', mirror=True,showspikes=True, spikemode='across', spikesnap='cursor',spikethickness=1,spikecolor='rgba(256,256,256,0.5)')
#fig.show(config = dict({'scrollZoom': True}))
plotly.offline.plot(fig, filename = 'Results.html', auto_open=False, config=dict(displayModeBar=True, scrollZoom = True))