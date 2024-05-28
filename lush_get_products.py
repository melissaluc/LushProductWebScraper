import requests
from bs4 import BeautifulSoup
from selenium import webdriver
import time
import re
import json

URLS = {
    "bath":"https://www.lush.ca/en/bath-shower/?cgid=bath-shower&start=0&sz=1000",
    "skincare":"https://www.lush.ca/en/skincare/?cgid=all-face&start=0&sz=1000",
    "body":"https://www.lush.ca/en/body/?cgid=all-body&start=0&sz=1000",
    "gift_sets":"https://www.lush.ca/en/gifts/all-gift-sets/?cgid=wrapped&start=0&sz=1000",
    "makeup":"https://www.lush.ca/en/makeup/makeup/"
    }

def getProducts(product, key):
    try:
        pid = product.select_one(".product")["data-pid"]
        img_url = product.select_one('picture source')['srcset'].split(',')[0].split(' ')[0]
        rating = product.select_one('.tile-reviews .stars > span').text.split(" ")[-1]
        number_of_ratings = product.select_one('.tile-reviews .empress').text
        category = product.select_one('.product-tile-category').text
        name = product.select_one('.product-tile-name').text.split("\n")[1]
        default_price=product.select_one('.tile-price').text
        default_size=product.select_one('.tile-size').text
        link = product.select_one(f'.product-tile-link-{pid}')['href']
        sizes = []

        # Extract product options
        options = product.find_all('button', class_='tile-selection-btn')
        
        for option in options:
            url = option['value']
            price = option.find('span', class_='tile-price').text.strip()
            size = option.find('span', class_='tile-size').text.strip()
            sizes.append({
                "size": size,
                "price": price,
                "url": url
            })
        
        data =  {
                    "pid":pid,
                    "name":name,
                    "main_category":key,
                    "sub_category":category,
                    "rating":rating,
                    "number_of_ratings":number_of_ratings,
                    "img_url":img_url,
                    "size":default_size,
                    "price":default_price
                    # "sizes":sizes
            }
        return data, f'http://lush.ca{link}'
    except Exception as e:
        return None
        pass


def getProductDetails(product):
      
    description = product.select_one(".top-description").text
    pid = product.select_one(".page")['data-querystring'].replace('pid=','')
    name = product.select_one(".product-name").text
    tagline = product.select_one(".tagline").text
    options = product.select_one(".size-attributes ").findChildren()
    ingredients=product.select_one('div.product-ingredients> span.ingredient-link-wrapper').text
    print(ingredients)
    sizes =[]
    for option in options:
        price = option.select_one('size-tile').select_one('.value')
        size = option.select_one('size-tile').select_one('span.name')
        sizes.append({
            "size":size,
            "price":price
        })
    return {
        "pid":pid,
        "name":name,
        "tagline":tagline,
        "description":description,
        "sizes":sizes
    }

      

product_links=[]
data =[]

for key in URLS:        
     
    page = requests.get(URLS.get(key), headers={
                'Accept': 'application/json, text/plain, */*',
                'Host':'www.lush.ca'})

    soup = BeautifulSoup(page.content, "html.parser")
    # print(soup)
    grid = soup.find("div", {"class": "product-grid"}).findChildren()
    for product in grid:
        d = getProducts(product,key)

        if d==None:
            pass
        else:
            data.append(d[0])
            product_links.append(d[1])
print(product_links)
data = [item for item in data if item is not None]
with open('lush_data.json', 'w', encoding ='utf8') as f:
    # data = json.dumps(data)
    json.dump(data, f,ensure_ascii = False)
    f.close


for link in product_links:
    page = requests.get(link, headers={
                'Accept': 'application/json, text/plain, */*',
                'Host':'www.lush.ca'})

    soup = BeautifulSoup(page.content, "html.parser")
    getProductDetails(product)
