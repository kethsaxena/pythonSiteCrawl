import os  
from selenium import webdriver  
from selenium.webdriver.common.keys import Keys  
from selenium.webdriver.chrome.options import Options  
import requests

from fake_useragent import UserAgent
import proxycrawl as pc

from bs4 import BeautifulSoup as bs

import urllib
import re  
import pandas as p
import csv as c
import numpy as np
import datetime as dt
from timeit import default_timer as timer
import time

start = timer()




chrome_options = Options()  
chrome_options.add_argument("--headless")  
chrome_options.binary_location = r"/usr/bin/google-chrome" 
driver = webdriver.Chrome(executable_path=os.path.abspath(r"/usr/bin/chromedriver"),   chrome_options=chrome_options)  


###INITIAL PARAMETERS
date="{:%Y%m%d}".format(dt.datetime.today())
projectFolder="/fledging/projects/min_hdl/output/July/"+date+"/run1"       
fileName="/fledging/projects/min_hdl/input/asinList.csv"


####FUNCTIONS
def getUniqueItem():
    ####TITLE
    title=soup.find("h1",{"class":"a-size-large a-spacing-none",
                    "role":"main"}) 
    strTitle=title.contents[2].strip()

    ###REVIEW RATING 
    try:
        rating=soup.find('span', {'class': "a-icon-alt"})
        strRating=(rating.contents[0].strip()).split(" ")[0]
    except:
        strRating=0


    ###REVIEW COUNT 
    try:
        div=soup.find('div', {'class': "a-section a-spacing-small"})
        totalRevCount=div.find('span', {'class': "a-size-small"})
        strRevCount=(totalRevCount.a.contents[0].strip()).split(" ")[0]
    except:
        strRevCount=0

    return [strTitle,strRating,strRevCount]
                

def modSheet(myrow,myCol,fileName):
    outFile=fileName
    with open(projectFolder+"/"+outFile, 'a',newline='') as f:
        p.DataFrame(data=myrow,columns=myCol).to_csv(f,header=False,index=False,columns=myCol,mode="a")
    f.close()




#####CODE RUN STARTS HERE########## 
data=p.read_csv(fileName,usecols=[0])
#print(data)
data["asin"]=data.iloc[:,0].map(lambda x:x.split("dp/")[1])
#data=data.loc[data["asin"]=="B07NBLJTL6",:]
asinlist=list(data.iloc[:,1].unique())
#print(asinlist)

#problem 

#asinlist= [x for x in asinlist if x not in ["B075H9G1CH","B01AINESJM"]]

#asinlist=[x for x  in asinlist if x in ["B075H9G1CH","B01AINESJM"]]

urlList=[]
for item in asinlist:
    urlList.append("https://www.amazon.com/gp/offer-listing/"+item)

# for item in asinlist:
#     print("https://www.amazon.com/gp/offer-listing/"+item)



#INTIAL TABLES 
listNot=[]
listYes=[]
listFull=[]

counterln=0
counterFl=1
for counter,item in enumerate(urlList):
    listYes=[]
    time.sleep(3)
    print("Running on item: " +str(counter+1)+" "+str(item))
    actualUrl=item
    asin=actualUrl.split("offer-listing/")[1]
    try:
        #print(actualUrl,counter)
        url = urllib.parse.quote_plus(actualUrl)
        #url='https%3A%2F%2Fwww.amazon.com%2Fdp%2FB07K1J3C23'
        url = "https://api.proxycrawl.com/?token=njgXAEQhxH5x_XgMAMtBOg&page_wait=1000&url=%s"%(url)
        ua = UserAgent()
        header = {"user-agent": ua.random}
        page = requests.get(url, headers=header)
        soup = bs(page.content, "lxml")
        
        ###SCRAP THE DOCS   
        try:
            div=soup.find('div', {'id': "olpOfferListColumn"})
            if re.sub(r'\s+', '',div.p.contents[0])=="Currently,therearenosellersthatcandeliverthisitemtoyourlocation.":
                print("listing not Found MF!")
                raise Exception
            else:
                pass
        except Exception:
            raise RuntimeError 
        else:  
            rows=div.findAll('div', {"role": "row",
                                        "class": "a-row a-spacing-mini olpOffer"
                                        })
            
            uniqueItem=getUniqueItem()                            


            for counter,elem in enumerate(rows):
                time.sleep(3)
                row=[]
                price=elem.find('span',{'class':"a-size-large a-color-price olpOfferPrice a-text-bold"})
                condition=elem.find('span',{'class':"a-size-medium olpCondition a-text-bold"})
                
                #LINK,TITLE,RATING, REVCOUNT, ASIN
                row.append(actualUrl)
                row.append(actualUrl.split("offer-listing/")[1])
                row.append(uniqueItem[0])
                row.append(uniqueItem[1])
                row.append(uniqueItem[2])
                
                
                #PRICE,CONDITION
                try:
                    strPrice=price.contents[0].strip()
                    strCondition=re.sub("[^A-Za-z0-9]+", "", condition.contents[0].strip())
                    row.append(strPrice)
                    row.append(strCondition)
                except:
                    strPrice=np.nan
                    strCondition="condNF"
                    row.append(strPrice)
                    row.append(strCondition)

                #SELLER    
                try:
                    sellerSpan=elem.find("div",{"class":"a-column a-span2 olpSellerColumn"}).find("span",{"class":"a-size-medium a-text-bold"})
                    strSeller=re.sub(r'[^\w]', '',sellerSpan.a.contents[0]).lower()        
                    #row.append(strSeller) 
                except (AttributeError):
                    sellerSpan=elem.find('div',{'class':"a-column a-span2 olpSellerColumn"}).find('img',alt=True)
                    strSeller=re.sub(r'\s+', '',sellerSpan['alt']).lower()
                    #row.append(strSeller)
                except:
                    strSeller="sellerNF"
                    
                
                finally:
                    row.append(strSeller)
                    #print("item for "+str(counter)+":"+strSeller)
                
                ###FULFILLMENT & joinkey
                try:
                    fFilltag=elem.find('div',{'class':"a-column a-span3 olpDeliveryColumn"}).find("span",{"data-action":"a-popover"})               
                    strfFill=re.sub(r'\s+', '',fFilltag.a.contents[0]).lower()
                except: 
                    strfFill="fulFillSELF"
                finally:
                    #print("item for "+str(counter)+":"+strfFill)
                    row.append(strSeller+"_"+strfFill+"_"+asin)
            
                colsLS=["link","asin","title",
                        "qty","rev","price",
                        "condition","seller","joinkey"]
                listYes.append([row])
                
                modSheet(listYes[counter],colsLS,"AMZ_NonQty_ListSuccess.csv") 
                print(listYes[counter])
                #table.append(row)
               
    except RuntimeError:
        counterln+=1
        print("Fail on item: " +str(counter+1)+" with asin:"+asin)
        colsLF=["asin","url"]
        
        listNot.append([asin,actualUrl])
        #data_df = p.DataFrame(data=listNot)
        modSheet([listNot[counterln-1]],colsLF,"AMZ_NonQty_Fail_list.csv")
     
        
end = timer()
print(end - start)


driver.close()
