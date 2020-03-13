'''Celery task for scrapping data'''
import re
import os
from celery.task.schedules import crontab
from celery.decorators import periodic_task
from celery.utils.log import get_task_logger

import requests
from bs4 import BeautifulSoup
from .models import Jumia


LOGGER = get_task_logger(__name__)


@periodic_task(run_every=(crontab(minute=os.environ.get('CELERY_TIME', ''))),
               name="task_scrap_jumia",
               ignore_result=True)
def task_scrap_jumia():
    try:
        Jumia.objects.all().delete()
        soup = scrap_data_jumia()
        nav = soup.select('.itm')
        categories = []
        all_products = []
        for item in nav:
            if item.get('href'):
                category = {
                    'link': item['href']
                }
                categories.append(category)

        total_length = 0
        for category in categories:
            link = "https://www.jumia.co.ke"+category['link']
            soup = scrap_data_jumia_categories(category, link)
            if soup:
                products = soup.find_all(class_="sku")
                product_details = sort_product_details_out(products, category)
                total_length += product_details['length'] 
                all_products.append(product_details['prods'])
                get_pagination_data(soup)
    except ValueError as e_x:
        LOGGER.info(e_x, 'Didnt succeed')
        print(e_x)




'''
Get pagination data
'''
def get_pagination_data(soup):
    for x in soup.find_all('section',attrs={'class':'pagination'}):
        for b in x.find_all('a', attrs={"title":"Next"}, href=True):
            if b.get('href'):
                print(b.get('href'))


'''
Get products from every category
'''
def scrap_data_jumia_categories(category, url):
    if(category['link'].startswith('/')):
        page = requests.get(url)
        soup = BeautifulSoup(page.content, 'html.parser')
        return soup

'''
Get catrgories
'''
def scrap_data_jumia():
    page = requests.get("https://www.jumia.co.ke/")
    soup = BeautifulSoup(page.content, 'html.parser')
    return soup


'''
Sort product details into meaningful information
'''
def sort_product_details_out(products, category):
    prods = []
    for product in products:
        try:
            old_price, new_price, discount_percentage = find_prices(product)
            link = find_links(product)
            image = find_image(product)
            discount = float(old_price)-float(new_price)
            prod = {
                'old_price': old_price,
                'new_price': new_price,
                'discount_percentage': discount_percentage,
                'link': link,
                'image': image,
                'discount': discount,
                'category': category
            }
            new_jumia_prod = Jumia(
                name="",
                old_price=str(old_price),
                new_price=str(new_price),
                discount=str(discount),
                discount_percentage=str(discount_percentage),
                link=link,
                image=image,
                category=category
            )
            new_jumia_prod.save()
            prods.append(prod)
        except Exception as e:
            print(e)
    return {'length':len(prods), 'prods': prods}



'''
Find image helper
'''
def find_image(product):
    for img in product.find_all('img', attrs={'src': re.compile("^https://")}):
        return img.get('src')

''''
Find links helper
'''
def find_links(product):
    for link in product.find_all('a',href=True):
        return link.get('href')

'''
Find prices and discounts from product
'''
def find_prices(product):
    for a in product.find_all(class_='price-container'):
        x =a.find_all(text=True)
        old_price = 0
        new_price = 0
        discount_percentage = 0
        if(x[0] != ' '):
            old_price = x[-3].replace(',', '')
            new_price = x[-8].replace(',', '')
            discount_percentage = float(x[0].strip('%')) * -1
        else:
            old_price = x[-5].replace(',', '')
        return old_price, new_price, discount_percentage
