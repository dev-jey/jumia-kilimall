from django.shortcuts import render
import pandas as pd
import numpy as np
from .models import AllData
from django.http import HttpResponse
from django.db.models import Q
import requests
from bs4 import BeautifulSoup
from django.core.paginator import Paginator


def index(request):
    '''
    Get all records and render them to the user
    '''
    try:
        products = AllData.objects.all()
        if not products:
            return render(request, 'crawlers/index.html', {'products': [], 'total_length': 0})
        qualified_products = sort_products(products.values())
        print(qualified_products)
        for p in qualified_products:
            print(p)
        paginator = Paginator(qualified_products.to_dict(orient='records'), 60)
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        return render(request, 'crawlers/index.html', {'page_obj': page_obj})
    except BaseException as e:
        print(e)

def search(request):
    '''
    Get all records and render them to the user searched
    '''
    search = request.GET.get('key') or ''
    try:
        products = AllData.objects.filter(Q(name__contains=search) | Q(brand__contains=search)).values()
        if not products:
            return render(request, 'crawlers/index.html', {'products': [], 'total_length': 0})
        qualified_products = sort_products(products)
        paginator = Paginator(qualified_products.to_dict(orient='records'), 60)
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        return render(request, 'crawlers/search.html', {'page_obj': page_obj, 'qualified_products':qualified_products})
    except BaseException as e:
        print(e)


def sort_products(products):
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
    return qualified_products