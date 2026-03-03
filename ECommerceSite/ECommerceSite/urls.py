"""
URL configuration for ECommerceSite project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from . import views
from django.contrib.sitemaps.views import sitemap
from django.contrib.sitemaps import GenericSitemap
from .sitemaps import StaticViewSitemap, product_info_dict
handler403 = 'ECommerceSite.views.custom_403_view'

sitemaps = {
    'static': StaticViewSitemap,
    'produse': GenericSitemap(product_info_dict, priority=0.6), # GenericSitemap cerut
}
urlpatterns = [
    path('account/', include('Account.urls')),
    path('admin/', admin.site.urls),
    path('', include('Home.urls')),
    path('products/', include('Products.urls')),
    path('cart/', include('Cart.urls')),
    path('promotii/',include('Promotions.urls')),
    path('interzis/', views.test_interzis_view, name='test_interzis'),
    path('sitemap.xml', sitemap, {'sitemaps': sitemaps},name='django.contrib.sitemaps.views.sitemap'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
