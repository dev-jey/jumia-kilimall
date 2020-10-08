from django.shortcuts import render
import pandas as pd
import numpy as np
from .models import AllData
from django.http import HttpResponse
import requests
from bs4 import BeautifulSoup
from django.core.paginator import Paginator


def index(request):
    '''
    Get all records and render them to the user
    '''
    try:
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
        paginator = Paginator(qualified_products.to_dict(orient='records'), 60)
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        return render(request, 'crawlers/index.html', {'page_obj': page_obj})
    except BaseException as e:
        print(e)

