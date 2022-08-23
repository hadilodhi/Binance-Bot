from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.support.select import Select
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from datetime import date
from dateutil.relativedelta import relativedelta
import time
import csv

# Setting parameters for selenium to work
options = webdriver.ChromeOptions()
options.add_argument("--start-maximized")
driver = webdriver.Chrome(options=options)
driver.get('http://scstrade.com/MarketStatistics/MS_HistoricalPrices.aspx')

# Setting ids
company = driver.find_element_by_id("txtSearch")
start = driver.find_element_by_id("date1")
end = driver.find_element_by_id("date2")
price = driver.find_element_by_id("btn1")

# Setting company
company.click()
company.send_keys("TRG")
time.sleep(2)
company.send_keys(Keys.DOWN)
company.send_keys(Keys.ENTER)

#Setting start date
enddate = (date.today()).strftime("%b/%d/%Y")
start.click()
start.send_keys('01/01/2000')
start.send_keys(Keys.ENTER)

#Setting end date
end.click()
end.send_keys(enddate)
end.send_keys(Keys.ENTER)

price.click()

time.sleep(10)
#driver.implicitly_wait(5)
driver.quit()
