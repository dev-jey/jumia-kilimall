from django.urls import include, path
from jkm.crawlers import views

urlpatterns = [
    path('', views.index, name='main-view'),
    path('search/', views.search, name='search-view')
]