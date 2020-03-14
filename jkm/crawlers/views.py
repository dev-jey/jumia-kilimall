from django.shortcuts import render
from .models import Jumia
from .tasks import task_scrap_jumia


def index(request):
    '''
    Get all records and render them to the user
    '''
    products = Jumia.objects.all()
    return render(request, 'crawlers/index.html', {'products': products, 'total_length': len(products)})
