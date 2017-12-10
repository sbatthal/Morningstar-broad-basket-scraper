# -*- coding: utf-8 -*-
"""
Created on Sun Dec 10 10:30:09 2017

@author: SIVAKUMAR BATTHALA
"""

import bs4 as bs
import requests
import pandas as pd
# url link
url = 'http://news.morningstar.com/fund-category-returns/commodities-broad-basket/$FOCA$BB.aspx'
# read url
resp = requests.get(url)
# parse html using beautifulsoup
soup = bs.BeautifulSoup(resp.text, "html.parser")
# use the contentTable
#Table_alt = soup.find_all('table', id='contentTable')
# find table in soup
table = soup.find("table")
# find all rows
rows = table.find_all("tr")

# Initialize
table_contents = []   # store your table here
for tr in rows:
    # First one is the header row
    if rows.index(tr) == 0 : 

        #row_headers = ([ th.find("a").get('sortitem') for th in tr.find_all('th') if th.find("a").get('sortitem') != '' ])
        # get row headers by looking for tag th
        row_headers = ([ th.getText().strip() for th in tr.find_all('th') if th.getText().strip() != '' ])
       
    else : 
        
        # row_cells = ([ tr.find("a").get('href') ] if tr.find("a") else [] ) + [ td.getText().strip() for td in tr.find_all('td') if td.getText().strip() != '' ] 
        #row_cells = [ td.find("a").get('href') + td.getText().strip() for td in tr.find_all('td') if td.getText().strip() != '' ] 
        Tablerows = []
        allrows = tr.find_all('td')
        for td in allrows:
            # First row is the one with link to each ticker
            if allrows.index(td) == 0 : 
                if tr.find("a"):
                    # Look for a tag and get text next to href tag
                   rowvalues = td.find("a").get('href')
                else :
                    # For category header look for b tag
                   rowvalues = td.find("b").getText()
                               
            else:
                # if not first row, just get the text
               rowvalues = td.getText().strip()
               # Build the list
            Tablerows += [rowvalues]
            # Category header has ticker empty..so accomodate it
        if(len(allrows) < 8):
                print(Tablerows)
                tempTablerows = []
                tempTablerows.append(Tablerows[0])
                tempTablerows.append(str('  '))
                # use extend
                tempTablerows.extend(Tablerows[1:])
                Tablerows = tempTablerows
                
        table_contents.append(Tablerows)
            
# Create a dataframe using pandas
df = pd.DataFrame.from_records(table_contents, columns=row_headers)
# Write to excel
df.to_excel('MorningStar_Commodity_Funds.xlsx')             