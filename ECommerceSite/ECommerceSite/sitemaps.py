from django.contrib.sitemaps import Sitemap
from django.urls import reverse
from Products.models import Product

class StaticViewSitemap(Sitemap):
    priority = 0.5
    changefreq = 'daily'

    def items(self):
        return ['home', 'login', 'register', 'promotii', 'products']

    def location(self, item):
        return reverse(item)

product_info_dict = {
    'queryset': Product.objects.all(),
    'date_field': 'date_added',
}