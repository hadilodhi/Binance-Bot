from bs4 import BeautifulSoup
from pandas import DataFrame
from tabulate import tabulate
import pandas as pd
import os
cwd = os.getcwd()
datadir = cwd + r"\Data.csv"

table = []
with open('Historical Prices - SCSTrade.com provides prices history of over a decade.html', 'r') as html_file:
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
df = df.iloc[:-7]
df["time"] = pd.to_datetime(df["time"])
df["time"]= df["time"].dt.date
df.set_index('time', inplace=True)
#print(tabulate(df, headers='keys', tablefmt='psql'))
df.to_csv(datadir,index=False, header=True)