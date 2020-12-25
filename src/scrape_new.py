import requests
import re
from bs4 import BeautifulSoup
import pandas as pd

from datetime import datetime

URL = 'https://www.onedayonly.co.za'
headers = {
    'User-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.61 Safari/537.36'
}

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


def str_to_float(s)->float:
    return float(re.sub('[^0-9.\-]','',s))

def extract_prices(product_tag):
    
    prices_div = product_tag.find('div', {'class': 'css-zzliqo'})
    
    if not prices_div:
        print('Could not find prices div')
        return None, None
    
        
    retail = (prices_div
              .find('h2', {'color': 'darkGrey', 'class': re.compile('css-.*-GalleryProduct')})
              .get_text())
    
    selling = (prices_div
              .find('h2', {'color': 'black', 'class': re.compile('css-.*-GalleryProduct')})
              .get_text())
    
    retail = str_to_float(retail)
    selling = str_to_float(selling)
    
    return retail, selling



def extract_product_info(product):
    
    product_obj = {}
    
    brand, title = extract_product_detail(product)
    
    product_obj['brand'] = brand
    product_obj['shortname'] = title
    
    retail, selling = extract_prices(product)
    
    product_obj['price_retail'] = retail
    product_obj['price_selling'] = selling
    
    return product_obj


def to_csv(df, today):
    f = '../data/{}.csv'.format(today)
    print(f)
    df.to_csv(f)


def main():
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

    to_csv(df, today)


if __name__ == '__main__':
    main()
