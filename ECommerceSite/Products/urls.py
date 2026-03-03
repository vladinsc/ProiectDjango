from django.urls import path
from . import views
from Account import views as AW


urlpatterns = [
    path('', views.index, name='products'),
    path('addProduct/', views.addProductView, name='addProduct'),
    path('claim_offer/', AW.claim_offer, name='claim_offer'),
    path('oferta/', AW.pagina_oferta, name='pagina_oferta'),
    path('category/<slug:category_slug>/', views.index, name='products_category'),
    path('<slug:slug>/', views.product, name='product'),
    path('addToCart/<int:prodid>/', views.addToCartView, name='addToCart'),


]