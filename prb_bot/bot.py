"""prb-7c5a
1079
S_MINING
MiningIdle
[2022-07-20T02:14:15+00:00] Now the worker should be mining.
2013984
2013984
13669220
80c49e257ad1aee1baa0d9cbfd653318e85de9092361a197be2c07226d8c6210
29991.45784432
29899.992
526
480
822.5303 PHA
0.2.4
848b954d581c2fa60b1024cc7f3a1322b4ca027f
259769843
116386694
305324032
43E9fDcVqJ1emFyhK6BBFvZom93zMxFgKk244PBaht5jZKF8
ff260777-fe50-4209-a815-0d73d4c556e9"""

from bs4 import BeautifulSoup
from selenium import webdriver
import time

driver = webdriver.Chrome("/Users/lkyeyoon/phala_bot/prb_bot/chromedriver")
URL = "http://kyleprb.tplinkdns.com:3000/lifecycle/status/QmXfr7DANxDxteEkzrUhDJQe3htMczxL3uQ1wt3UBH8oCb"
driver.get(URL)
time.sleep(3)
html = driver.page_source


#soup = BeautifulSoup(html)
#prb_list = soup.find_all("tr", "ka-tr ka-row")

bsObj = BeautifulSoup(html, "html.parser")

for sibling in bsObj.find("tbody",{"class":"ka-tbody"}).tr.next_siblings:

  print(sibling)
  print()


#print(soup)
print('=========')
#print(prb_list[0])



#for row in prodList:
#  print(row)