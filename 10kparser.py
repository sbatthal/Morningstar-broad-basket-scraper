# -*- coding: utf-8 -*-
"""
Created on Tue Jul  4 12:52:22 2017

@author: SIVAKUMAR BATTHALA
"""
import csv
Col1 = "CIK"
Col2 = "FundNames"
Col3 = "FileType"
Col4 = "FileDate"
Col5 = "Link"

mydictionary={Col1:[], Col2:[], Col3:[], Col4:[], Col5:[]}
csvFile = csv.reader(open(r"D:\13f\2014q2\master.idx", "r"),delimiter='|')
for row in csvFile:
  mydictionary[Col1].append(row[0])
  mydictionary[Col2].append(row[1])
  mydictionary[Col3].append(row[2])
  mydictionary[Col4].append(row[3])
  mydictionary[Col5].append(row[4])
  
  
