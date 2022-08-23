import os
import pandas as pd
from tabulate import tabulate
import subprocess

cwd = os.getcwd()
datadir = cwd + r"\Data.csv"

timeframes  = {0:{'name':'10 years', 'period':2500},1:{'name':'5 years', 'period':1250}, 2:{'name':'4 years', 'period':1000}, 3:{'name':'3 years', 'period':750}, 4:{'name':'2 years', 'period':500}, 5:{'name':'1 year', 'period':250}, 6:{'name':'6 months', 'period':120}}
tests = {'DoubleMA', 'TripleMA', 'TripleEMA', 'MA+MACD', 'MA+MACD+RSI'}

def run(cmd):
    subprocess.Popen(['python', cmd]).wait()

def loop():
    for test in tests:
        run('Backtest' + test + '.py')
        run('Results' + test + '.py')
        try:
            os.remove("MAs.json")
        except:    
            pass
        try:
            os.remove("parameters.json")
        except:    
            pass

def move(direc):
    os.mkdir(direc)
    for test in tests:
        os.rename('Results' + test + ".html", direc + "/" + 'Results' + test + ".html")

run("parse.py")
loop()
move('Alldata')
for timeframe in timeframes:
    df = pd.read_csv(datadir)
    df = df.tail(timeframes[timeframe]['period'])
    df.to_csv(datadir,index=False, header=True)
    loop()
    move(timeframes[timeframe]['name'])
try:
    os.remove("MAs.json")
except:    
    pass
try:
    os.remove("parameters.json")
except:    
    pass
try:
    os.remove("Data.csv")
except:    
    pass

