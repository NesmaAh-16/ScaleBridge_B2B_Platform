from django.urls import path
from . import views

app_name = 'operations'

urlpatterns = [
    path('buying-circles/', views.buying_circle_list, name='buying_circle_list'),
]