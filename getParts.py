import os
import sys
from datetime import datetime
import pandas as pd
from urllib.request import urlopen, Request
from bs4 import BeautifulSoup
import simplejson
import logging
import sqlite3 as sql

sys.path.append('lib')
from scrape_html import request_url

# ----- variables ------
base_url = "https://octopart.com"
database = "data/data.db"

# keyword-list ["keyword1", "keyword2", ...]
keywords = ["ATMEGA8", "S1G-E3/61T"]      
    

# ----- function get_part_info -----

def get_part_info(keyword):

    try:
        search_url = base_url + "/search?q=" + keyword + "&currency=EUR&specs=0" 
        html_0 = request_url(search_url)
        parsed_0 = BeautifulSoup(html_0, features="html.parser")
        nametag = parsed_0.find('mark')
        part_name = nametag.string
        part_detail_url = base_url + nametag.parent.parent.parent.get('href')
        
        html_1 = request_url(part_detail_url)
        parsed_1 = BeautifulSoup(html_1, features="html.parser")
        text = "See all price breaks »"
        price_detail_url = parsed_1.find_all(lambda tag: tag.name == "a" and text in tag.text)[0].get('href')
        part_shortdesc = parsed_1.find('p', attrs={'class':'short-description'}).string
        
        logging.info(f" Successfully retrieved part info for keyword {keyword}")
        
        return part_name, part_shortdesc, price_detail_url
       
    except:
        
        logging(f" Error while retrieving part info for keyword {keyword}")

    
# ---- retrieve part info for given keywords ----


list = []

for keyword in keywords:
    part = get_part_info(keyword)
    part_info = dict(
        name=part[0],
        shortdesc=part[1],
        price_url=part[2])

    list.append(part_info)

parts_df = pd.DataFrame(list)


# ----- write to database -----

conn = sql.connect(database)
parts_df.to_sql(name='parts', con=conn, index=False, if_exists="replace")
conn.close()
