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

# ----- function get_price_list -----

def get_price_list(price_url, keyword):
    html_2 = request_url(price_url)
    parsed_2 = BeautifulSoup(html_2, features="html.parser")
    
    rows = parsed_2.find_all('tr', attrs={'class':'offerRow'})
    
    list = []
    
    for row in rows:
        seller_obj = row.find('td', attrs={'class':'col-seller'})
        sku_obj = row.find('td', attrs={'class':'col-sku'}).find('a')
        avail_obj = row.find('td', attrs={'class':'col-avail'})
        type_obj = row.parent.find_previous_sibling().h3.string    
        price_obj = row.find('td', attrs={'class':'pdp-all-breaks-price-cell'})
        if price_obj:
            currency = price_obj.get('data-currency')
            price = price_obj.string
        else:
            currency = 'n/a'
            price = 0

        if avail_obj and (avail_obj.string is not None):
            try:
                stock_int = int(avail_obj.string.replace(',',''))
            except:
                stock_int = 0
        else:
            stock_int = 0

        parsetime = datetime.now()    

        price_info = dict(
            parsetime=parsetime,
            part_name=keyword,
            seller=seller_obj.string,
            type=type_obj.string,
            sku=sku_obj.string.replace('\n',''),
            stock=avail_obj.string,
            stock_int = stock_int,
            currency=currency,
            price=price
        )

        list.append(price_info)
    
    return list
    
    
# ----- read part list from database -----

conn = sql.connect(database)
c = conn.cursor()
c.execute('SELECT * FROM parts')
data = c.fetchall() 

price_table = pd.DataFrame()

for row in data:
    price_url = base_url + row[2]
    prices = pd.DataFrame(get_price_list(price_url, row[0]))
    price_table = price_table.append(prices)


# ----- write to database -----
    
conn = sql.connect(database)
price_table.to_sql(name='prices', con=conn, index=False, if_exists="append")
conn.close()