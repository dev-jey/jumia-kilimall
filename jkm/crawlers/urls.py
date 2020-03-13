from django.urls import include, path
from jkm.crawlers import views

urlpatterns = [
    path('', views.index, name='main-view')
]