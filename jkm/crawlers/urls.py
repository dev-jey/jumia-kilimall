from django.urls import include, path
from jkm.crawlers import views
from django.contrib import admin


admin.site.site_header = 'Jumia Kilimall Masoko'
admin.site.site_title = 'Jumia Kilimall Masoko Products Bot'

urlpatterns = [
    path('', views.index, name='main-view'),
    path('search/', views.search, name='search-view')
]