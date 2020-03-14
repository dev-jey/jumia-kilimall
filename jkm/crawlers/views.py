from django.shortcuts import render
from .models import Jumia
from .tasks import task_scrap_jumia
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
from django.http import HttpResponse


def index(request):
    '''
    Get all records and render them to the user
    '''
    products = Jumia.objects.all()
    return render(request, 'crawlers/index.html', {'products': products, 'total_length': len(products)})
    # return HttpResponse('James')
