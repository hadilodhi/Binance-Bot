import pandas as pd
import os
from tabulate import tabulate
import numpy as np
import plotly.graph_objects as go
import plotly
import json
import pandas_ta as ta

f = open('MAs.json')
MAs = json.load(f)

cwd = os.getcwd()
datadir = cwd + r"\Data.csv"

df = pd.read_csv(datadir, index_col='Time', parse_dates=True)

ma_short = MAs['MA1']['0']
ma_medium = MAs['MA2']['0']
ma_long = MAs['MA3']['0']

df['MA_' + str(ma_short)] = ta.sma(df["Close"], length=ma_short)
df['MA_' + str(ma_medium)] = ta.sma(df["Close"], length=ma_medium)
df['MA_' + str(ma_long)] = ta.sma(df["Close"], length=ma_long)
df.loc[(df.iloc[:, 4] > df.iloc[:, 5]) & (df.iloc[:, 5] > df.iloc[:, 6]),['buy']] = 1
df.loc[(df.iloc[:, 4] < df.iloc[:, 5]) & (df.iloc[:, 5] < df.iloc[:, 6]),['buy']] = 0
df = df.ffill()
df['duplicate'] = df['buy'].shift(1)
df['buy'] = df.apply(lambda x: np.nan if x['buy'] == x['duplicate'] \
                          else x['buy'], axis=1)
df = df.drop('duplicate', axis=1)
df['percentage'] = df['buy']
df.loc[(df['percentage'] == 0),['percentage']] = 1
df['sell'] = df['buy']
df.loc[(df['buy'] == 1),['buy']] = df['Close']
df.loc[(df['sell'] == 0),['sell']] = df['Close']
df.loc[(df['percentage'] == 1),['percentage']] = df['Close']
df['location'] = df['percentage'].shift(1)
df = df.ffill()
df.loc[(df['sell'] == 1),['sell']] = 0
df['percentage'] = df.apply(lambda x: x['percentage'] if x['percentage'] != x['location'] \
                        else np.nan, axis=1)
df['location'] = df.apply(lambda x: np.nan if pd.isnull(x['percentage']) \
                        else x['location'], axis=1)
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
df['percentage'] = df.apply(lambda x: - x['percentage'] if x['sell'] == 0 and x['buy'] != 0 and pd.notnull(x['location'])\
                        else x['percentage'], axis=1)
df2 = df[['percentage']]
df2 = df2.dropna()
df['percentage'] = df.apply(lambda x: str(x['percentage']) + ' %' if pd.notnull(x['percentage'])\
                        else x['percentage'], axis=1)
df.replace(0, np.nan, inplace=True)
df2["return"] = df2["percentage"].cumsum()
df2["drawdown"] = df2["return"] - df2["return"].cummax()

print("MA Config    ", ma_short,",", ma_medium, ",", ma_long)
print("Profit       ", round(df2['return'].max(), 2), "%")
print("Hold Return ", round((df.Close[-1] - df.Close[0]) / df.Close[0] * 100, 2), "%")
print("Drawdown    ", round(df2["drawdown"].min(), 2), "%")
print("Win Rate     ", round(len(df2.loc[df2.percentage > 0]) / len(df2.index) * 100, 2), "%")
print("Exposure     ", round((df['buy'].count() + df['sell'].count()) / len(df.index) * 100, 2), "%")
print("Duration     ", (df.index[-1] - df.index[0]).days, "days")
print("No of Trades ", len(df2.index))
print(tabulate(df, headers='keys', tablefmt='psql'))

layout = dict(
    title='Bitcoin Triple SMA Strategy',
    title_x=0.5,
    xaxis_title="DateTime",
    yaxis_title="USD ($)",
    legend_title="Plots",
    xaxis=dict(
        rangeselector=dict(
            buttons=list([
                dict(count=12,
                    label='12hr',
                    step='hour',
                    stepmode='backward'),
                dict(count=1,
                    label='1D',
                    step='day',
                    stepmode='backward'),
                dict(count=7,
                    label='7D',
                    step='day',
                    stepmode='backward'),
                dict(count=14,
                    label='14D',
                    step='day',
                    stepmode='backward'),
                dict(count=1,
                    label='1M',
                    step='month',
                    stepmode='backward'),
                dict(step='all')
            ]),
            x=0.45
        ),
        rangeslider=dict(
            visible = True
        ),
        type='date'
    )
)

fig = go.Figure(layout=layout)
fig.add_trace(
    go.Ohlc(x=df.index,
    open=df['Open'],
    high=df['High'],
    low=df['Low'],
    close=df['Close'],
    name="OHLC"))
fig.add_trace(
    go.Scatter(x=df.index,
    y=df.iloc[:, 4],
    line=dict(color='orange'),
    name=str(df.columns[4])))
fig.add_trace(
    go.Scatter(x=df.index,
    y=df.iloc[:, 5],
    line=dict(color='blue'),
    name=str(df.columns[5])))
fig.add_trace(
    go.Scatter(x=df.index,
    y=df.iloc[:, 6],
    line=dict(color='green'),
    name=str(df.columns[6])))
fig.add_trace(
    go.Scatter(x=df.index,
    y=df['buy'],
    line=dict(color='green'),
    name='Buy'))
fig.add_trace(
    go.Scatter(x=df.index,
    y=df['sell'],
    line=dict(color='red'),
    name='Sell'))
fig.add_trace(
    go.Scatter(x=df.index,
    y=df['location'],
    mode="markers+text",
    name="Percentages",
    text=df['percentage'],
    textposition="middle right"))
fig.add_annotation(text=
                "MA Config       " + str(ma_short) + "," + str(ma_medium) + "," + str(ma_long) + '<br>' +
                "Profit              " + str(round(df2['return'].max(), 2)) + " %" + '<br>' +
                "Hold Return   " + str(round((df.Close[-1] - df.Close[0]) / df.Close[0] * 100, 2)) + " %" + '<br>' + 
                "Drawdown     " + str(round(df2["drawdown"].min(), 2)) + " %" + '<br>' +
                "Win Rate        " + str(round(len(df2.loc[df2.percentage > 0]) / len(df2.index) * 100, 2)) + " %" + '<br>' +
                "Exposure        " + str(round((df['buy'].count() + df['sell'].count()) / len(df.index) * 100, 2)) + " %" + '<br>' + 
                "Duration         " + str((df.index[-1] - df.index[0]).days) + ' days<br>' + 
                "No of Trades   " + str(len(df2.index)),
                align='left',
                showarrow=False,
                xref='paper',
                yref='paper',
                x=0.05,
                y=0.05,
                bordercolor='blue',
                borderwidth=1)
fig.update_yaxes(
    autorange = True,
    fixedrange = False
)                   
#fig.show(config = dict({'scrollZoom': True}))
plotly.offline.plot(fig, filename = 'Results.html', auto_open=False, config=dict(displayModeBar=True, scrollZoom = True))
