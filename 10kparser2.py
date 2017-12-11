# -*- coding: utf-8 -*-
"""
Created on Sat Jul  8 22:51:35 2017

@author: SIVAKUMAR BATTHALA
"""

import os, sys, csv, re
import requests
from bs4 import BeautifulSoup
import datetime
import pandas

def Download_Master_Index_Files():
    current_year = datetime.date.today().year
    current_quarter = (datetime.date.today().month - 1) // 3 + 1
    start_year = 2016
    years = list(range(start_year, current_year))
    quarters = ['QTR1', 'QTR2', 'QTR3', 'QTR4']
    history = [(y, q) for y in years for q in quarters]
    for i in range(1, current_quarter + 1):
        history.append((current_year, 'QTR%d' % i))
    urls = ['https://www.sec.gov/Archives/edgar/full-index/%d/%s/master.idx' % (x[0], x[1]) for x in history]
    #urls.sort()
    filenames = ['%d_%s.pkl' % (x[0], x[1]) for x in history]
    # Download the master index file and split lines and store in a dataframe
    for index, url in enumerate(urls):
        lines = requests.get(url).text.splitlines()
        records = ([(line.split('|')) for line in lines[11:]])
        df = pandas.DataFrame(records,columns=['CIK','CompanyName','FormType','FilingDate','urllink'])
        df['urllink'] = 'https://www.sec.gov/Archives/' + df['urllink']
        df.to_pickle(filenames[index])

def Process_10k_Files(file):
    df = pandas.read_pickle(file)
    keyformtypes = ['10-K']
    idx = df[df['FormType'].isin(keyformtypes)].index.tolist()
    newdf = df.loc[idx]
    newdf = newdf.reset_index(drop=True)
    print(len(newdf))
    FinalDict={}
    page=[]
    Table = []
    s_FinalDict = {}
    #len(newdf)
    for index in range(0,3):
        print(index)
        urllink = newdf['urllink'][index]
        print(urllink)
        page = get_page(urllink)   
        #Item 1
        regexs = ('bold;\">\s*Item 1\.(.+?)bold;\">\s*Item 1A\.',   #<===pattern 1: with an attribute bold before the item subtitle
              'b>\s*Item 1\.(.+?)b>\s*Item 1A\.',               #<===pattern 2: with a tag <b> before the item subtitle
              'Item 1\.\s*<\/b>(.+?)Item 1A\.\s*<\/b>',         #<===pattern 3: with a tag <\b> after the item subtitle          
              'Item 1\.\s*Business\.\s*<\/b(.+?)Item 1A\.\s*Risk Factors\.\s*<\/b',#<===pattern 4: with a tag <\b> after the item+description subtitle %%!
              'Item 1\.\s*Business(.+?)Item 1A\.\s*Risk Factors') 
        Item1,Table = Extract_10k_Text(regexs,page)
        print(Table)
        FinalDict['url'] = urllink
        #FinalDict['htmlurl'] =  
        FinalDict['Item1'] = {'Text': Item1, 'table' : Table}
        #Item 1A
        regexs = ('bold;\">\s*Item 1A\.(.+?)bold;\">\s*Item 1B\.',   #<===pattern 1: with an attribute bold before the item subtitle
                      'b>\s*Item 1A\.(.+?)b>\s*Item 1B\.',               #<===pattern 2: with a tag <b> before the item subtitle
                      'Item 1A\.\s*<\/b>(.+?)Item 1B\.\s*<\/b>',         #<===pattern 3: with a tag <\b> after the item subtitle          
                      'Item 1A\.\s*Risk Factors\.\s*<\/b(.+?)Item 1B\.\s*Unresolved\.\s*<\/b', #<===pattern 4: with a tag <\b> after the item+description subtitle %%!%%!        
                      'Item 1A\.\s*Risk Factors(.+?)Item 1B\.\s*Unresolved')
        Item1A,Table = Extract_10k_Text(regexs,page)
        FinalDict['Item1A'] = {'Text': Item1A, 'table' : Table}
        regexs = ('bold;\">\s*Item 2\.(.+?)bold;\">\s*Item 3\.',   #<===pattern 1: with an attribute bold before the item subtitle
                      'b>\s*Item 2\.(.+?)b>\s*Item 3\.',               #<===pattern 2: with a tag <b> before the item subtitle
                      'Item 2\.\s*<\/b>(.+?)Item 3\.\s*<\/b>',         #<===pattern 3: with a tag <\b> after the item subtitle          
                      'Item 2\.\s*Properties\.\s*<\/b(.+?)Item 3\.\s*Legal\.\s*<\/b', #<===pattern 4: with a tag <\b> after the item+description subtitle %%!%%!        
                      'Item 2\.\s*Properties(.+?)Item 3\.\s*Legal')
        Properties,Table = Extract_10k_Text(regexs,page)
        FinalDict['Properties'] = {'Text': Properties, 'table' : Table}

        regexs = ('bold;\">\s*Item 7\.(.+?)bold;\">\s*Item 7A\.',   #<===pattern 1: with an attribute bold before the item subtitle
                      'b>\s*Item 7\.(.+?)b>\s*Item 7A\.',               #<===pattern 2: with a tag <b> before the item subtitle
                      'Item 7\.\s*<\/b>(.+?)Item 7A\.\s*<\/b>',         #<===pattern 3: with a tag <\b> after the item subtitle
                      '\n[ \t]*?ITEM[ \t]*?7A\.[ \t]*?(Qualitative|Quantitative)[ \t]*?and[ \t]*?(Qualitative|Quantitative)',
                      'Item 7\.\s*\.\s*<\/b(.+?)Item 7A\.\s*Quantitative\.\s*<\/b', #<===pattern 4: with a tag <\b> after the item+description subtitle %%!%%!        
                      'Item 7\.\s*(.+?)Item 7A\.\s*Quantitative')
        mda,Table = Extract_10k_Text(regexs,page)
        FinalDict['mda'] = {'Text': mda, 'table' : Table}
        
        s_FinalDict[index]=FinalDict
    return s_FinalDict,page,Table
             
def get_page(urllink):
        page = requests.get(urllink).content
        page = page.decode('utf-8')
        page = page.strip()  #<=== remove white space at the beginning and end
        page = page.replace('\n', ' ') #<===replace the \n (new line) character with space
        page = page.replace('\r', '') #<===replace the \r (carriage returns -if you're on windows) with space
        page = page.replace('&nbsp;', ' ') #<===replace "&nbsp;" (a special character for space in HTML) with space. 
        page = page.replace('&#160;', ' ') #<===replace "&#160;" (a special character for space in HTML) with space.
        while '  ' in page:
            page = page.replace('  ', ' ') #<===remove extra space       
        return page

def Get_All_Tables(soup):
    tabledict = {}
    tables = soup.findAll("table")
    for index,table in enumerate(tables):
     if table.findParent("table") is None:
         tabledict[index] = table
    return tabledict            
                               
def Extract_10k_Text(regexs,page):
    outText = []
    Table = []       
    for regex in regexs:
        match = re.search(regex, page, flags=re.IGNORECASE)  #<===search for the pattern in HTML using re.search from the re package. Ignore cases.
        print(regex)    
        print(match)              
        #If a match exist....
        if match is not None:
            #Now we have the extracted content still in an HTML format
            #We now turn it into a beautiful soup object
            #so that we can remove the html tags and only keep the texts
            
            soup = BeautifulSoup(match.group(1), "html.parser") #<=== match.group(1) returns the texts inside the parentheses (.*?) 
            print('I am here')
            #Table = Get_All_Tables(soup)
            Table = parseTable(match.group(1))
            
            #soup.text removes the html tags and only keep the texts
            #rawText = soup.text.encode('utf8') #<=== you have to change the encoding the unicodes
            outText = soup.text
           
            #remove space at the beginning and end and the subtitle "business" at the beginning
            #^ matches the beginning of the text
            #outText = re.sub("\s*","",rawText.strip(),flags=re.IGNORECASE)
            
            break
    return outText,Table

def parseTable(html):
    #Each "row" of the HTML table will be a list, and the items
    #in that list will be the TD data items.
    ourTable = []

    #We keep these set to NONE when not actively building a
    #row of data or a data item.
    ourTD = None    #Stores one table data item
    ourTR = None    #List to store each of the TD items in.


    #State we keep track of
    inTable = False
    inTR = False
    inTD = False

    #Start looking for a start tag at the beginning!
    tagStart = html.find("<", 0)

    while( tagStart != -1):
        tagEnd = html.find(">", tagStart)

        if tagEnd == -1:    #We are done, return the data!
            return ourTable

        tagText = html[tagStart+1:tagEnd]

        #only look at the text immediately following the <
        tagList = tagText.split()
        tag = tagList[0]
        tag = tag.lower()

        #Watch out for TABLE (start/stop) tags!
        if tag == "table":      #We entered the table!
            inTable = True
        if tag == "/table":     #We exited a table.
            inTable = False

        #Detect/Handle Table Rows (TR's)
        if tag == "tr":
            inTR = True
            ourTR = []      #Started a new Table Row!

        #If we are at the end of a row, add the data we collected
        #so far to the main list of table data.
        if tag == "/tr":
            inTR = False
            ourTable.append(ourTR)
            ourTR = None

        #We are starting a Data item!
        if tag== "td":
            inTD = True
            ourTD = ""      #Start with an empty item!

        #We are ending a data item!
        if tag == "/td":
            inTD = False
            if ourTD != None and ourTR != None:
                cleanedTD = ourTD.strip()   #Remove extra spaces
                ourTR.append( cleanedTD)
            ourTD = None


        #Look for the NEXT start tag. Anything between the current
        #end tag and the next Start Tag is potential data!
        tagStart = html.find("<", tagEnd+1)

        #If we are in a Table, and in a Row and also in a TD,
        # Save anything that's not a tag! (between tags)
        #
        #Note that this may happen multiple times if the table
        #data has tags inside of it!
        #e.g. <td>some <b>bold</b> text</td>
        #
        #Because of this, we need to be sure to put a space between each
        #item that may have tags separating them. We remove any extra
        #spaces (above) before we append the ourTD data to the ourTR list.
        if inTable and inTR and inTD:
            ourTD = ourTD + html[tagEnd+1:tagStart] + " "
            #print("td:", ourTD)   #for debugging


    #If we end the while loop looking for the next start tag, we
    #are done, return ourTable of data.
    return(ourTable)