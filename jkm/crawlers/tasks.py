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
            if category['link'].startswith("/") and category['link'].endswith('/'):
                link = f"https://www.jumia.co.ke{category['link']}?page=1"
                soup = scrap_data_jumia_categories(category, link)
                pages = get_pagination_data(soup)
                for i in range(1, int(pages)+1):
                    link = f"https://www.jumia.co.ke{category['link']}?page={i}"
                    print('\n\n\n', link, '\n\n\n\n\n')

                    soup_ = scrap_data_jumia_categories(category, link)
                    if soup_:
                        persist_to_db(soup_, category, total_length, all_products)
    except ValueError as e_x:
        LOGGER.info(e_x, 'Didnt succeed')
        print(e_x)

def persist_to_db(soup, category, total_length, all_products):
    '''
    Save items to the database
    '''
    products = soup.find_all(class_="sku")
    product_details = sort_product_details_out(products, category)
    total_length += product_details['length'] 
    all_products.append(product_details['prods'])

def get_pagination_data(soup):
    '''
    Get pagination data
    '''
    pages = 1
    for x in soup.find_all('section',attrs={'class':'pagination'}):
        try:
            pages = x.find_all('a', href=True)[:-1][-1].text
        except:
            pass
    return pages

def scrap_data_jumia_categories(category, url):
    '''
    Get products from every category
    '''
    if(category['link'].startswith('/')):
        page = requests.get(url)
        soup = BeautifulSoup(page.content, 'html.parser')
        return soup

def scrap_data_jumia():
    '''
    Get catrgories
    '''
    page = requests.get("https://www.jumia.co.ke/")
    soup = BeautifulSoup(page.content, 'html.parser')
    return soup

def sort_product_details_out(products, category):
    '''
    Sort product details into meaningful information
    '''
    prods = []
    for product in products:
        try:
            # print(product)
            old_price, new_price, discount_percentage = find_prices(product)
            total_ratings, avg_rating = find_ratings(product)
            brand, product_name = find_name(product)
            link = find_links(product)
            image = find_image(product)
            discount = float(old_price)-float(new_price)
            prod = {
                'name': product_name,
                'total_ratings': total_ratings,
                'brand': brand,
                'old_price': old_price,
                'new_price': new_price,
                'discount_percentage': discount_percentage,
                'link': link,
                'image': image,
                'discount': discount,
                'category': category
            }
            Jumia.objects.update_or_create(
                name=product_name,
                brand=brand,
                total_ratings=str(total_ratings),
                avg_rating=str(avg_rating),
                old_price=str(old_price),
                new_price=str(new_price),
                discount=str(discount),
                discount_percentage=str(discount_percentage),
                link=link,
                image=image,
                category=category
                )
            prods.append(prod)
        except Exception as e:
            print(e)
    return {'length':len(prods), 'prods': prods}

def find_ratings(product):
    '''
    Find total number of ratings and ratings per product
    '''
    total_ratings = 0
    avg_rating = 0
    for item in product.find_all(class_='total-ratings'):
        values = item.find_all(text=True)
        total_ratings = ''.join(values).strip('()') 
    for item in product.find_all(class_='stars'):
        avg_rating = round(int(item['style'].split()[-1].replace("%", ""))/100 * 5, 1)
    return total_ratings, avg_rating

def find_image(product):
    '''
    Find image helper
    '''
    for img in product.find_all('img', attrs={'src': re.compile("^https://")}):
        return img.get('src')

def find_links(product):
    ''''
    Find links helper
    '''
    for link in product.find_all('a',href=True):
        return link.get('href')

def find_prices(product):
    '''
    Find prices and discounts from product
    '''
    for a in product.find_all(class_='price-container'):
        x = a.find_all(text=True)
        old_price = 0
        new_price = 0
        discount_percentage = 0
        if x[0] != ' ':
            old_price = x[-3].replace(',', '')
            new_price = x[-8].replace(',', '')
            discount_percentage = float(x[0].strip('%')) * -1
        else:
            old_price = x[-5].replace(',', '')
        return old_price, new_price, discount_percentage

def find_name(product):
    '''
    Get name details of a product
    '''
    for item in product.find_all(class_='title'):
        name = item.find_all(text=True)
        brand = name[0]
        product_name = name[-1]
        return brand, product_name
