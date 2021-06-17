from django.urls import path
from . import views

# apikey path will get the api key
# api path will display the company data in candlestick chart format
urlpatterns = [
    path('', views.home, name="stock-api-home"),
    path('home/', views.home, name="stock-api-home"),
    path('apikey/', views.apikey, name="stock-api-key"),
    path('api/', views.api, name="stock-api-request"),
]