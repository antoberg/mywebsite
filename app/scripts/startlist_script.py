import requests
from bs4 import BeautifulSoup as bs
import pandas as pd
import re

def get_startlist(url):
    response = requests.get(url)
    soup = bs(response.content, "lxml") #données html brutes
    
    body = soup.find("section",{"class" : "startlist"})
    riders = body.find_all("li",{"class": "startlist-rider"})
    race_ID = soup.find('body', id='article-show')['data-article']
    race_name = soup.find('div', {"class" : 'main'}).h1.text
    
    
    r_urls=[]
    r_name=[]
    r_number=[]
    for r in riders:
        r_urls.append(r.a['href'])
        row_name = r.a.text
        row_name = row_name.replace('\n', '')
        row_name = re.sub(r"([A-Z])", r" \1", row_name).strip()
        r_name.append(row_name)
         #dossard
        r_number.append(r.find("em", {"class" : "startlist-number"}).text)
        
    df_startlist=pd.DataFrame({
        'name': r_name,
        'url' : r_urls,
        'number' : r_number
        })
    
    print('Partants scrapés avec succès pour : '+race_name)
    return  df_startlist, race_ID, race_name