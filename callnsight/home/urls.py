from django.contrib import admin
from django.urls import path,include
from home import views

pp_name = 'home'
urlpatterns = [
    path('',views.main, name='home'),
    path('loading/',views.loading, name='loading'),
    path('result/<str:result_type>/', views.result, name='result'),
    path('error/',views.error, name='error'),
]