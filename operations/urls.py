from django.urls import path
from . import views

app_name = 'operations' # This MUST match the include call

urlpatterns = [

    path('catalog/', views.product_list, name='product_list'),
    path('catalog/add/', views.product_create, name='product_create'),
    path('catalog/edit/<int:pk>/', views.product_update, name='product_update'),
    path('catalog/delete/<int:pk>/', views.product_delete, name='product_delete'),
    path('marketplace/', views.marketplace_list, name='marketplace'),
    path('circles/', views.buying_circle_list, name='buying_circle_list'),
]
