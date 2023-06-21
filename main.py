from collections import namedtuple
from decimal import Decimal
from urllib.parse import urlparse, parse_qsl

import requests
# noinspection PyPackageRequirements
from attrdict import AttrDict
from bs4 import BeautifulSoup
from fake_useragent import UserAgent
from icecream import ic

DEFAULT_HEADERS = {'User-Agent': UserAgent().chrome}
Product = namedtuple('Product', ['name', 'price'])


def parse_ztore(url):
    r = requests.get(url, headers=DEFAULT_HEADERS, timeout=10)
    soup = BeautifulSoup(r.text, 'lxml')
    e = soup.find('div', {'class': 'name'}).find('h2')
    name = e.text

    e = soup.find('div', {'class': 'price'}).find('span')
    price = Decimal(e.text.strip('$'))
    ic(name, price)
    return Product(name, price)


def parse_hktvmall(url):
    r = requests.get(url, headers=DEFAULT_HEADERS, timeout=10)
    soup = BeautifulSoup(r.text, 'lxml')
    e = soup.find('h1', {'class': 'last'})
    name = e.text.split('#')[0].strip()

    e = soup.find('div', {'class': 'price'}).find('span')
    price = Decimal(e.text.strip('$').strip(' '))
    ic(name, price)
    return Product(name, price)


def parse_uniqlo(url):
    parsed_url = urlparse(url)
    query_params = dict(parse_qsl(str(parsed_url.query)))
    product_code = query_params['productCode']

    spu_url = f'https://www.uniqlo.com.hk/data/products/spu/zh_HK/{product_code}.json'
    r = requests.get(spu_url, headers=DEFAULT_HEADERS, timeout=10)
    data = AttrDict(r.json())
    name = data.summary.name

    price_url = f'https://d.uniqlo.com.hk/p/product/i/product/spu/pc/query/{product_code}/zh_HK'
    r = requests.get(price_url, headers=DEFAULT_HEADERS, timeout=10)
    data = AttrDict(r.json())
    price = Decimal(str(data.resp[0].summary.minPrice))
    ic(name, price)
    return Product(name, price)


def parse(url):
    parsed_url = urlparse(url)
    host = parsed_url.netloc
    parsers = {
        'www.ztore.com': parse_ztore,
        'www.hktvmall.com': parse_hktvmall,
        'www.uniqlo.com.hk': parse_uniqlo,
    }
    if host not in parsers:
        raise NotImplementedError(f'{host} has not been implemented yet!')
    parser = parsers[host]
    product = parser(url)
    ic(product)


if __name__ == '__main__':
    # parse_ztore('https://www.ztore.com/tc/product/bold-jell-aromatic-floral-sabon-fragrance-body-1054370')
    # parse_hktvmall('https://www.hktvmall.com/hktv/zh/main/%E6%BB%B4%E9%9C%B2/s/H1010002/%E8%AD%B7%E7%90%86%E4%BF%9D%E5%81%A5/%E8%AD%B7%E7%90%86%E4%BF%9D%E5%81%A5/%E5%80%8B%E4%BA%BA%E8%AD%B7%E7%90%86%E7%94%A8%E5%93%81/%E6%89%8B%E9%83%A8%E8%AD%B7%E7%90%86/%E6%BD%94%E6%89%8B%E6%B6%B2/%E6%BB%B4%E9%9C%B2%E7%B6%93%E5%85%B8%E6%9D%BE%E6%9C%A8%E6%AE%BA%E8%8F%8C%E6%BD%94%E6%89%8B%E6%B6%B2500g-%E6%96%B0%E8%88%8A%E5%8C%85%E8%A3%9D%E9%9A%A8%E6%A9%9F%E7%99%BC%E9%80%81-%E6%B4%97%E6%89%8B%E6%B6%B2-%E6%AE%BA%E8%8F%8C-%E6%B6%88%E6%AF%92-/p/H0888001_S_10003187')
    # parse_uniqlo('https://www.uniqlo.com.hk/zh_HK/product-detail.html?productCode=u0000000026079&searchFlag=true')
    parse('https://www.ztore.com/tc/product/bold-jell-aromatic-floral-sabon-fragrance-body-1054370')
    parse('https://www.hktvmall.com/hktv/zh/main/%E6%BB%B4%E9%9C%B2/s/H1010002/%E8%AD%B7%E7%90%86%E4%BF%9D%E5%81%A5/%E8%AD%B7%E7%90%86%E4%BF%9D%E5%81%A5/%E5%80%8B%E4%BA%BA%E8%AD%B7%E7%90%86%E7%94%A8%E5%93%81/%E6%89%8B%E9%83%A8%E8%AD%B7%E7%90%86/%E6%BD%94%E6%89%8B%E6%B6%B2/%E6%BB%B4%E9%9C%B2%E7%B6%93%E5%85%B8%E6%9D%BE%E6%9C%A8%E6%AE%BA%E8%8F%8C%E6%BD%94%E6%89%8B%E6%B6%B2500g-%E6%96%B0%E8%88%8A%E5%8C%85%E8%A3%9D%E9%9A%A8%E6%A9%9F%E7%99%BC%E9%80%81-%E6%B4%97%E6%89%8B%E6%B6%B2-%E6%AE%BA%E8%8F%8C-%E6%B6%88%E6%AF%92-/p/H0888001_S_10003187')
    parse('https://www.uniqlo.com.hk/zh_HK/product-detail.html?productCode=u0000000026079&searchFlag=true')
