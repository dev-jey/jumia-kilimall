from django.shortcuts import render
import pandas as pd
import numpy as np
import re
import os
from .models import AllData, Sites
from .tasks import sort_products, get_category_url, get_star_rating
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from selenium import webdriver
from celery.utils.log import get_task_logger
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options

from django.http import HttpResponse
import requests
from bs4 import BeautifulSoup

LOGGER = get_task_logger(__name__)

def index(request):
    '''
    Get all records and render them to the user
    '''
    task_scrap_kilimall1()
    
    products = AllData.objects.filter().values()
    if not products:
        return render(request, 'crawlers/index.html', {'products': [], 'total_length': 0})
    df = pd.DataFrame(list(products))
    arr = np.array(df['avg_rating'].tolist())
    df['avg_rating']=pd.to_numeric(arr, errors='coerce') 
    arr = np.array(df['new_price'].tolist())
    df['new_price']=pd.to_numeric(arr, errors='coerce') 
    arr = np.array(df['total_ratings'].tolist())
    df['total_ratings']=pd.to_numeric(arr, errors='coerce') 
    df['avg_rating'] = df['avg_rating'].replace(0, np.NaN)
    # the mean rating across all products
    C = df['avg_rating'].mean()
    #filter out qualified products
    r=df['new_price']
    m = df['avg_rating'].quantile(0.25)
    qualified_products = df.copy().loc[df['avg_rating'] >= m]
    v = qualified_products['total_ratings']
    R = qualified_products['avg_rating']
    qualified_products['score'] = (v/(v+m) * R) + (m/(m+v) * C) + ((r*v/r) * C)
    qualified_products.sort_values(by=['score'], inplace=True, ascending=False)
    return render(request, 'crawlers/index.html', {'products': qualified_products, 'total_length': len(qualified_products)})


def task_scrap_kilimall1():
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