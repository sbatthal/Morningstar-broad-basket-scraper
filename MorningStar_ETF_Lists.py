# -*- coding: utf-8 -*-
"""
Created on Sun Dec 10 10:30:09 2017

@author: SIVAKUMAR BATTHALA
"""

import bs4 as bs
import requests
import pandas as pd
# url link
url = 'http://news.morningstar.com/etf/Lists/ETFReturns.html?topNum=All&lastRecNum=10000&curField=8&category=0'
# read url
resp = requests.get(url)
# parse html using beautifulsoup
soup = bs.BeautifulSoup(resp.text, "html.parser")
# use the contentTable
#Table_alt = soup.find_all('table', id='contentTable')
# find table in soup
table = soup.findAll("table")
table = table[2]
# find all rows
rows = table.find_all("tr")

table_contents = []   # store your table here
for tr in rows:
    if rows.index(tr) == 0 : 
        row_cells = [ th.getText().strip() for th in tr.find_all('th') if th.getText().strip() != '' ]  
    else : 
        row_cells = ([ tr.find('th').getText() ] if tr.find('th') else [] ) + [ td.getText().strip() for td in tr.find_all('td') if td.getText().strip() != '' ] 
    if len(row_cells) > 1 : 
        table_contents += [ row_cells ]
            
# Create a dataframe using pandas
row_headers = table_contents[0]
del row_headers[2]
df = pd.DataFrame.from_records(table_contents, columns=table_contents[0])
# Write to excel
df.to_excel('MorningStar_Commodity_Funds.xlsx')             