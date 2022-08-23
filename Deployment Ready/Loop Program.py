import pause
from datetime import datetime, timedelta
import os,time
from dateutil.relativedelta import relativedelta

def ceil_dt(dt, delta):
    return dt + (datetime.min - dt) % delta

while 1:
    for x in range(0,48):
        now = datetime.now()
        stoptill = ceil_dt(now, timedelta(minutes=30))
        # stoptill = (now + relativedelta(seconds=10)).strftime("%Y-%m-%d %H:%M:%S")
        # stoptill = datetime.strptime(stoptill, "%Y-%m-%d %H:%M:%S")
        print('Waiting till',stoptill)
        pause.until(stoptill)
        os.system("Program.py")
    print('Recalibrating.....')
    os.system("retrievedata.py")
    time.sleep(20)
    os.system("Backtest.py")