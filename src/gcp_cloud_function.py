
import re
import os
import requests
import pandas as pd
from bs4 import BeautifulSoup

from google.cloud import storage

from datetime import datetime

URL = 'https://www.onedayonly.co.za'
headers = {
    'User-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.61 Safari/537.36'
}

BUCKET_NAME = os.environ.get('BUCKET_NAME')

def str_to_float(s) -> float:
    return float(re.sub('[^0-9.\-]', '', s))


def extract_prices(product_tag):
    
    prices_div = product_tag.find('div', {'class': 'css-zzliqo'})
    
    if prices_div is None:
        print('Could not find prices div')
        return None, None
    
    
    try:
        retail = (prices_div
                  .find('h2', {'color': 'darkGrey', 'class': re.compile('css-.*-GalleryProduct')})
                  .get_text())
        retail = str_to_float(retail)
    except AttributeError:
        print('Warning: Could not find retail price.')
        retail = None
    
    
    try:
        selling = (prices_div
                  .find('h2', {'color': 'black', 'class': re.compile('css-.*-GalleryProduct')})
                  .get_text())
        selling = str_to_float(selling)
    except AttributeError:
        print('Warning: Could not find selling price.')
        selling = None
    
    
    return retail, selling


def extract_product_detail(product_tag):

    product_divs = product_tag.find_all('div', {'class': re.compile('css-.*-GalleryProduct')})
    
    brand, title = None, None
    for div in product_divs:
        h2_tags = div.select('div h2')
        if h2_tags:
            assert len(h2_tags) == 2, 'Found more than 2 h2 tags'
            brand = h2_tags[0].get_text()
            title = h2_tags[1].get_text()
            
    return brand, title


def extract_product_info(product):
    
    product_obj = {}
    
    brand, title = extract_product_detail(product)
    
    product_obj['brand'] = brand
    product_obj['shortname'] = title
    
    retail, selling = extract_prices(product)
    
    product_obj['price_retail'] = retail
    product_obj['price_selling'] = selling

    product_obj['url'] = 'www.onedayonly.co.za' + product.get('href')

    return product_obj


def upload_blob(df, f):

    client = storage.Client()
    bucket = client.get_bucket(BUCKET_NAME)

    bucket.blob(f).upload_from_string(df.to_csv(), 'text/csv')

    return True

def run():
    now = datetime.now()
    today = str(now.date())

    page = requests.get(URL, headers=headers)

    soup = BeautifulSoup(page.content, 'html.parser')

    products = soup.find_all('a', class_='gallery-item')

    product_info = {'data': [], 'meta': {'date': today}}
    for product in products:
        if not product or ('onenightonly' in product.get('href')):
            continue
        product_info['data'].append(extract_product_info(product))

    df = pd.DataFrame(product_info['data'])
    df['date'] = product_info['meta']['date']

    f = '{}.csv'.format(today)
    upload_blob(df, f)

    return 



def main(req):

    run()