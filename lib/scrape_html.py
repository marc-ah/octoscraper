from urllib.request import urlopen, Request
import logging

# ----- functions -----
def request_url(url):
    try:   
        request = Request(
        url,
        headers={
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:55.0) Gecko/20100101 Firefox/55.0'})
        html = urlopen(request).read().decode()
        
        logging.info(f" Successfully read data from {url}")
        
        return html

    except:
        logging.error(f" An Error occured while requesting {url}")
        logging.error(f" ")