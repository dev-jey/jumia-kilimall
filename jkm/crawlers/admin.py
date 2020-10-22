from django.contrib import admin
from django.contrib.admin import AdminSite
from django.utils.translation import ugettext_lazy

from .models import AllData, Sites

admin.site.register(AllData)
admin.site.register(Sites)

# Register your models here.
class MyAdminSite(AdminSite):
    # Text to put at the end of each page's <title>.
    site_title = ugettext_lazy('Jumia Kilimall Masoko')

    # Text to put in each page's <h1> (and above login form).
    site_header = ugettext_lazy('Jumia Kilimall Masoko')

    # Text to put at the top of the admin index page.
    index_title = ugettext_lazy('Jumia Kilimall Masoko')

admin_site = MyAdminSite()