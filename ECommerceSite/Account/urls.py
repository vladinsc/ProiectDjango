from django.urls import path
from . import views
from django.contrib.auth import views as auth_views
urlpatterns = [
    path('register/', views.register, name='register'),
    path('login/', views.login_view, name='login'),
    path('', views.index, name='account'),
    path('logout/', auth_views.LogoutView.as_view(next_page=''), name='logout'),
    path('updateUserProfile/', views.updateUserProfile, name='updateUserProfile'),
    path('confirma_email/<str:cod>/', views.confirm_email_view, name='confirma_email'),
]