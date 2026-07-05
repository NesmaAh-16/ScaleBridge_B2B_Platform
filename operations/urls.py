from django.urls import path
from . import views

app_name = 'operations'

urlpatterns = [
    # Product catalog
    path('catalog/', views.product_list, name='product_list'),
    path('catalog/add/', views.product_create, name='product_create'),
    path('catalog/edit/<int:pk>/', views.product_update, name='product_update'),
    path('catalog/delete/<int:pk>/', views.product_delete, name='product_delete'),

    # Marketplace
    path('marketplace/', views.marketplace_list, name='marketplace'),

    # Buying Circles
    path('circles/', views.buying_circle_list, name='buying_circle_list'),
    path('circles/<int:pk>/', views.circle_detail, name='circle_detail'),
    path('circles/start/<int:product_pk>/', views.circle_create, name='circle_create'),
    path('circles/<int:pk>/join/', views.circle_join, name='circle_join'),
    path('circles/<int:pk>/leave/', views.circle_leave, name='circle_leave'),
    path('orders/<int:order_id>/update/', views.update_order_status, name='update_order_status'),
    path('orders/<int:order_id>/', views.order_detail, name='order_detail'),

    # 2. ADD THIS LINE: This allows the review button to work later
    path('orders/<int:order_id>/review/', views.leave_review, name='leave_review'),

    # 3. ADD THIS LINE: For the notification API
    path('api/notifications/unread/', views.notification_unread_count, name='unread_notifications'),
    path('ledger/', views.order_ledger_view, name='order_ledger'),
]


