from bs4 import BeautifulSoup
from pandas import DataFrame
from tabulate import tabulate
import pandas as pd
import os
cwd = os.getcwd()
datadir = cwd + r"\Data.csv"

table = []
with open('basedata.html', 'r') as html_file:
    content = html_file.read()
    soup = BeautifulSoup(content, 'lxml')
    rows = soup.find_all('tr')
    for row in rows:
        tablerow = []
        for column in row:
            tablerow.append(column.text.strip())
        if len(tablerow) == 7:
            table.append(tablerow)
df = DataFrame(table,columns=["time","open","high","low","close","volume","change"])
df = df.iloc[2:]
df = df.iloc[:-6]
df["time"] = pd.to_datetime(df["time"])
#df["time"]= df["time"].dt.datetime
df = df.iloc[::-1]
df.reset_index(drop=True, inplace=True)
df['open']=df['open'].str.replace(',','')
df['high']=df['high'].str.replace(',','')
df['low']=df['low'].str.replace(',','')
df['close']=df['close'].str.replace(',','')
df["open"] = pd.to_numeric(df["open"], downcast="float")
df["high"] = pd.to_numeric(df["high"], downcast="float")
df["low"] = pd.to_numeric(df["low"], downcast="float")
df["close"] = pd.to_numeric(df["close"], downcast="float")
df = df.drop(['volume', 'change'], axis=1)
#print(tabulate(df, headers='keys', tablefmt='psql'))
df.to_csv(datadir,index=False, header=True)