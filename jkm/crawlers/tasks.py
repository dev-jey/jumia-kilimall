'''Celery task for scrapping data'''
import os
import re
from celery.schedules import crontab
from celery.decorators import periodic_task
from celery.utils.log import get_task_logger
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
# from django.http import HttpResponse
from jkm import celery_app
import requests
from bs4 import BeautifulSoup
from .models import AllData, Sites


LOGGER = get_task_logger(__name__)


'''
Jumia scrapping script by bs4
'''


@celery_app.task(name="scrap-jumia")
def task_scrap_jumia():
    try:
        soup = scrap_data_jumia()
        nav = soup.select('.itm')
        categories = []
        all_products = []
        for item in nav:
            if item.get('href'):
                if item['href'].startswith("/") and item['href'].endswith('/') and len(item.select('span.text')):
                    categories.append({
                        'name': item.select('span.text')[::-1][-1].text,
                        'link': item['href'],
                    })

        total_length = 0
        for category in categories:
            link = f"https://www.jumia.co.ke{category['link']}?page=1"
            soup = scrap_data_jumia_categories(category, link)
            pages = get_pagination_data(soup)
            for i in range(1, int(pages)+1):
                link = f"https://www.jumia.co.ke{category['link']}?page={i}"
                print('\n\n\n', link, '\n\n\n\n\n')

                soup_ = scrap_data_jumia_categories(category, link)
                if soup_:
                    persist_to_db(soup_, category['name'],
                                  total_length, all_products)
    except ValueError as e_x:
        LOGGER.info(e_x, 'Didnt succeed')
        print(e_x)


def persist_to_db(soup, category, total_length, all_products):
    '''
    Save items to the database
    '''
    products = soup.find_all(class_="-paxs")
    product_details = sort_product_details_out(products, category)
    total_length += product_details['length']
    all_products.append(product_details['prods'])


def get_pagination_data(soup):
    '''
    Get pagination data
    '''
    pages = 1
    for x in soup.find_all('section', attrs={'class': 'pagination'}):
        try:
            pages = x.find_all('a', href=True)[:-1][-1].text
        except:
            pass
    return pages


def scrap_data_jumia_categories(category, url):
    '''
    Get products from every category
    '''
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
    for product_group in products:
        for product in product_group.find_all(class_='prd'):
            try:
                old_price = find_prices(product)[0]
                new_price = find_prices(product)[1]
                discount_percentage = find_prices(product)[2]
                total_ratings = find_ratings(product)[0]
                avg_rating = find_ratings(product)[1]
                brand = find_name(product)[0]
                product_name = find_name(product)[1]
                link = f"https://www.jumia.co.ke{product['href']}"
                image = product.find('img')['data-src']
                discount = float(old_price)-float(new_price)
                prod = {
                    'name': product_name[0],
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
                print(prod)
                LOGGER.info("Saving " + category + " products to database....")
                jumia_site = Sites.objects.get(name="Jumia")
                AllData.objects.update_or_create(
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
                    site=jumia_site,
                    category=category
                )
                prods.append(prod)
            except Exception as e:
                print(e)
                pass
    return {'length': len(prods), 'prods': prods}


def find_ratings(product):
    '''
    Find total number of ratings and ratings per product
    '''
    total_ratings = product['data-dimension26']
    avg_rating = product['data-dimension27']
    return [total_ratings, avg_rating]



def find_prices(product):
    '''
    Find prices and discounts from product
    '''
    old_price = 0
    new_price = 0
    discount_percentage = 0
    if product.find(class_='old'):
        old_price = float(product.find(class_='old').find(text=True).replace('KSh ', '').replace(',', ''))
    if product.find(class_='prc')['data-oprc']:
        old_price = float(product.find(class_='prc')['data-oprc'].replace('KSh ', '').replace(',', ''))
    else:
        old_price = 0
    new_price = float(product.find(class_='prc').find(text=True).replace('KSh ', '').replace(',', ''))
    discount_percentage = float(product.find(class_='tag _dsct').find(text=True).strip('%'))
    return [old_price, new_price, discount_percentage]


def find_name(product):
    '''
    Get name details of a product
    '''
    name = product.find(class_='name').find(text=True).split(' ', 1)
    brand = name[0]
    product_name = name[1:]
    return [brand, product_name]


'''
Kilimall scrapping script by selenium
'''
@celery_app.task(name="scrap-kilimall")
def task_scrap_kilimall():
    chrome_options = Options()
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument("disable-infobars")
    chrome_options.add_argument("--disable-extensions")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-setuid-sandbox") 
    chrome_options.add_argument("--remote-debugging-port=9222")
    chrome_options.add_argument("--disable-dev-shm-usage")

    if os.environ.get('CURRENT_ENV') == 'production':
        chrome_options.binary_location = os.environ.get('GOOGLE_CHROME_BIN')
    
    if os.environ.get('CURRENT_ENV') == 'production':
        driver = webdriver.Chrome(executable_path=str(
            os.environ.get('CHROMEDRIVER_PATH')), options=chrome_options)
    else:
        driver = webdriver.Chrome(
            ChromeDriverManager().install(), options=chrome_options)

    driver.implicitly_wait(5)

    driver.get('https://www.kilimall.co.ke/new/')

    categories = driver.find_elements_by_class_name("cls_item_content")

    categories_links = [get_category_url(category) for category in categories]
    for category_name in categories_links:
        try:
            driver.implicitly_wait(5)
            print(category_name[[*category_name][0]])
            driver.get(category_name[[*category_name][0]])
            driver.implicitly_wait(15)
            sort_products(driver, category_name['gc_id'], category_name)
            gc_id = category_name['gc_id']
            pages = driver.find_element_by_class_name(
                "el-pager").find_elements_by_class_name("number")[-1].text
            for i in range(1, int(pages)+1):
                new_url = f'https://www.kilimall.co.ke/new/commoditysearch?c={gc_id}&page={i}'
                print(new_url)
                driver.get(new_url)
                driver.implicitly_wait(15)
                sort_products(driver, category_name['gc_id'], category_name)
        except Exception as e:
            print(e)
            print('Connection refused')


def get_category_url(category):
    '''Get url ids for categories'''
    gc_id = 1057

    if 'Electronics' in category.text:
        gc_id = 1250
    elif 'Computers' in category.text:
        gc_id = 1072
    elif 'Home' in category.text:
        gc_id = 1466
    elif 'Clothes' in category.text:
        gc_id = 1294
    elif 'Shoes' in category.text:
        gc_id = 1350
    elif 'Bags' in category.text:
        gc_id = 1385
    elif 'Sports' in category.text:
        gc_id = 1385
    elif 'Health' in category.text:
        gc_id = 1615
    elif 'Baby' in category.text:
        gc_id = 1504
    elif 'Office' in category.text:
        gc_id = 1563
    elif 'Automotive' in category.text:
        gc_id = 1603
    new_category = category.text.replace(' ', '%20').replace('&', '%26')
    return {category.text: f'https://www.kilimall.co.ke/new/commoditysearch?c={gc_id}&aside={new_category}&gc_id={gc_id}',
            'gc_id': gc_id}


def get_star_rating(product):
    '''
    Get a products average rating
    '''
    stars = []
    for i in product.find_element_by_class_name("rateList").find_elements_by_tag_name("i"):
        if i.get_attribute("style") == 'color: rgb(247, 186, 42);':
            stars.append(i)
    return len(stars)


def sort_products(driver, gc_id, category_name):
    '''Get products from categories and add them to an array'''
    data_ = driver.find_element_by_class_name('imgbox')
    products = data_.find_elements_by_class_name("el-col-6")
    try:
        for product in products:
            product_data = {}
            name = product.find_element_by_class_name("wordwrap").text
            avg_rating = get_star_rating(product)
            new_price = ''.join(product.find_element_by_tag_name(
                "span").text.split(' ')[::-1][0].split(','))
            discount_percentage = 0
            old_price = 0
            total_ratings = 0
            link = None
            image = None
            try:
                discount_percentage = product.find_element_by_class_name(
                    "greenbox").text.split(' ')[0].split('%')[0]
                old_price = ''.join(product.find_element_by_class_name(
                    "twoksh").text.split(' ')[::-1][0].split(","))
                total_ratings = product.find_element_by_class_name(
                    "sixtwo").text.replace('(', '').replace(')', '')
                link = product.find_element_by_class_name(
                    "showHand").get_attribute("href")
                # import pdb; pdb.set_trace()
                image = product.find_element_by_class_name(
                    "showHand").find_element_by_tag_name("img").get_attribute("src")
            except Exception as e:
                print(e)
                pass
            discount = int(old_price) - int(new_price)
            category = [*category_name][0]
            product_data = {'name': name,
                            'new_price': new_price,
                            'avg_rating': avg_rating,
                            "discount_percentage": discount_percentage,
                            "old_price": old_price,
                            "total_ratings": total_ratings,
                            'link': link,
                            "image": image,
                            "discount": discount,
                            'category': category}
            LOGGER.info("Saving " + category + " products to database....")
            kilimall_site = Sites.objects.get(name="Kilimall")
            AllData.objects.update_or_create(
                name=name,
                brand='',
                total_ratings=str(total_ratings),
                avg_rating=str(avg_rating),
                old_price=str(old_price),
                new_price=str(new_price),
                discount=str(discount),
                discount_percentage=str(discount_percentage),
                link=link,
                image=image,
                site=kilimall_site,
                category=category
            )
    except Exception as e:
        print(e)


celery_app.conf.beat_schedule = {
    # Execute every x minutes.
    'run-kilimall-task': {
        'task': 'scrap-kilimall',
        'schedule': crontab(minute=os.environ.get('CELERY_TIME_K', '')),
    },
    'run-jumia-task': {
        'task': 'scrap-jumia',
        'schedule': crontab(minute=os.environ.get('CELERY_TIME_J', '')),
    },
}
