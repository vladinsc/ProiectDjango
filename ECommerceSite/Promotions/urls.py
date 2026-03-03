from django.urls import path
from . import views


urlpatterns = [
    path('', views.creare_promotie, name='promotii'),
]