from django.urls import path
from . import views
from Orders.views import place_order


urlpatterns = [
    path('', views.viewcart, name='viewcart'),
    path('place_order/', place_order, name='place_order'),
]