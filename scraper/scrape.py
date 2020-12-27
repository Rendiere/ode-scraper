import requests
import re
from bs4 import BeautifulSoup
import pandas as pd

from datetime import datetime

URL = 'https://www.onedayonly.co.za'
headers = {
    'User-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.61 Safari/537.36'
}


def str_to_float(s) -> float:
    return float(re.sub('[^0-9.\-]', '', s))


def extract_brand(product):
    brand = product.find('h2', class_='brand').text

    assert type(brand) == str, 'Found non-text data during brand extraction'

    return brand


def extract_prices(product):
    prices = product.find('span', class_='prices')

    retail = prices.find('h6', class_='retail')
    selling = prices.find('h3', class_='selling')

    if selling:
        selling = str_to_float(selling.text)
    else:
        selling = None

    if retail:
        retail = str_to_float(retail.text)
    else:
        retail = None

    return {
        'retail': retail,
        'selling': selling
    }


def extract_savings(product):
    savings = product.find("span", class_='savings')

    if savings:
        return savings.find('h6', class_='amount').text

    else:
        return None


def extract_product_info(product):
    product_obj = {}

    product_obj['brand'] = extract_brand(product)
    product_obj['image_url'] = product.find('img', class_='image').attrs['src']
    product_obj['shortname'] = product.find('h2', class_='shortname').text
    product_obj['short_desc'] = product.find('p', class_='name').text

    prices = extract_prices(product)

    product_obj['price_retail'] = prices['retail']
    product_obj['price_selling'] = prices['selling']

    product_obj['savings'] = extract_savings(product)

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

    home = soup.find(id='home')

    products = home.find_all('a', class_='new_product_block')

    product_info = {'data': [], 'meta': {'date': today}}
    for product in products:
        product_info['data'].append(extract_product_info(product))

    df = pd.DataFrame(product_info['data'])
    df['date'] = product_info['meta']['date']

    to_csv(df, today)


if __name__ == '__main__':
    main()
