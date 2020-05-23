# -*- coding: utf-8 -*-
"""
Created on Fri May 15 21:44:44 2020

@author: James Strebler
"""
    
    
import time
import csv
from selenium import webdriver as driver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from datetime import datetime
from pyotp import *
import linecache
import socket
from bs4 import BeautifulSoup
#import sys

totalrecsout = 0
cityindex = 0 
sleeptime = 20

filepathnet = "Y:\Python\FB Output\\"
fbconstant = 'https://www.facebook.com'
mktplcconstant = 'https://www.facebook.com/marketplace/'
srchconstant = '/search/?query='
chrome_path = r"Y:\Python\chromedriver.exe"
mychrome_options = Options()
mychrome_options.add_argument("--disable-notifications");
WebD = driver.Chrome(chrome_path, options=mychrome_options)
WebD.maximize_window()

compname = socket.gethostname()
print('compname')

with open(r'Y:\Python\FB Files\searches.csv') as searchfile:
        searchlist = list(csv.reader(searchfile)) 
        
wait=WebDriverWait(WebD,(sleeptime))
now0 = str(datetime.now())
now = now0.replace(" ", "_").replace(".", "-").replace(":", "-")
outfile = filepathnet + "fbmkt" + now + '.csv'
print(outfile)
    
#read cities ============================================================
with open(r'Y:\Python\FB Files\cities.csv') as cityfile:
    citylist = list(csv.reader(cityfile))
totalcities = len(citylist) - 1
#read searches ==========================================================

totalsearches = len(searchlist) 

search_url = mktplcconstant

# Log in ==================================================================
try:
    WebD.get(search_url)
except:
    print('***** exception to getting the web page, trying 2nd try *******')
    time.sleep(sleeptime)
    WebD.get(search_url)
    
time.sleep(sleeptime)

logfile = (r'C:\Users\jystr\Documents\Anaconda Python\Facebook\gozer2.txt')
emale = linecache.getline(logfile, 1).rstrip('\n')
password = linecache.getline(logfile, 2).rstrip('\n')
gozer = linecache.getline(logfile, 3).rstrip('\n')

liname = wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="email"]')))
liname.send_keys(emale)
lipass = WebD.find_element_by_xpath('//*[@id="pass"]')
lipass.send_keys(password)
libutt = WebD.find_element_by_xpath('//*[@id="loginbutton"]')
libutt.click()
time.sleep(sleeptime/4)            

totp = TOTP(gozer)
token = totp.now()
codebox = wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="approvals_code"]')))

codebox.send_keys(token)
codebutt = WebD.find_element_by_xpath('//*[@id="checkpointSubmitButton"]')
codebutt.click()
confbutt = wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="checkpointSubmitButton"]')))
confbutt.click()

time.sleep(sleeptime/2)


#city loop is outer loop===========================================================
while cityindex <= totalcities: 
    urlcity0 = str(citylist[cityindex])
    outputcity = urlcity0.replace("['", "").replace("']", "")
    urlcity = outputcity.replace(" ", "%20")

    if urlcity == '106021666096708':
        outputcity = 'Toledo'
    elif urlcity == '104114042957938':
        outputcity = 'Akron'
    elif urlcity == '104023459634857':
        outputcity = 'Dayton'
    elif urlcity == '108160772537759':
        outputcity = 'Sandusky'
    elif urlcity == 'annarbor':
        outputcity = 'Ann Arbor'
    elif urlcity == 'fort-wayne':
        outputcity = 'Fort Wayne'
        
    searchflag='notdone'
    searchindex = 0
    
    print(outputcity)
    
    #product search loop============================================================
    while searchflag != 'done':
        #read searches===========================================================
        outsearch = str(searchlist[searchindex]).replace("['", "").replace("']", "")
        urlsearch = outsearch.replace(" ", "%20")
        
        #build URL and get new page==============================================
        search_url = mktplcconstant + urlcity + srchconstant +urlsearch
        try:
            WebD.get(search_url)
        except:
            print('***** exception to getting the web page, trying 2nd try *******')
            time.sleep(sleeptime)
            WebD.get(search_url)
        print(outsearch)    
        time.sleep(sleeptime)
 
        #put page into BS4===================================================================
        codez = WebD.page_source
        soup = BeautifulSoup(codez, 'html.parser')
        
        # Process the page  =============================================================
        for elementA0 in soup.findAll("a", {"class": '_1oem'}):
            try:            
                title0 = elementA0.find("div", {"id": 'marketplace-modal-dialog-title'})
                title0 = title0.text.replace (',', ';')
                title0 = title0.encode("utf-8", "replace")
                title0 = title0.decode("utf-8")
                print(title0)
            except:
                print ('*** hit except condition')
                continue
            
            price0 = elementA0.find("div", {"class": '_f3l'})
            price0 = price0.text
            
            location0 = elementA0.find("span", {"class": '_7yi'})
            location0 = location0.text
            
            link0 = elementA0['href']
            link0 = fbconstant + link0
            
            text0 = elementA0.text.replace(',', ';')
            text0 = text0.replace(',', ';').replace('/n', ';').replace('/r', ';')
            text0 = text0.encode("utf-8", "replace")
            text0 = text0.decode("utf-8")
            
            totalrecsout = totalrecsout + 1
            totalrecsout0 = str(totalrecsout)
            
            newrec = totalrecsout0 + ',' + outputcity + ',' + outsearch + ',' + title0 + ',' + \
                price0 + ',' + location0 + ',' + link0 + ',' + text0
                
            with open(outfile, "a", encoding="utf-8") as outz:
                outz.write(newrec + '\r')
            print(newrec)

        searchindex = searchindex + 1
        
        if searchindex >= totalsearches:
            searchflag = 'done'
            
    cityindex = cityindex + 1

outz.close()
print('success')
        