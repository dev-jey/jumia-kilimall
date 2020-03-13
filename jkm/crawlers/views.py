from django.shortcuts import render
from .models import Jumia


'''
The main index function 
'''
def index(request):
    products = Jumia.objects.all()
    return render(request, 'crawlers/index.html', {'products': products, 'total_length': len(products)})

