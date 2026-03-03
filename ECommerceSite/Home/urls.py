from django.urls import path
from . import views
urlpatterns=[
    path('',views.home,name='home'),
    path('info/',views.info,name='info'),
    path('log', views.log, name='log'),
    path('contact/', views.contact_view, name='contact'),
]