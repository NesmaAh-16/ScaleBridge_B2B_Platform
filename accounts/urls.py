from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('me/', views.profile_view, name='profile'),
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('dashboard/admin/', views.admin_dashboard_view, name='admin_dashboard'),
    path('dashboard/business/', views.business_dashboard_view, name='business_dashboard'),
    path('business/profile/', views.business_profile, name='business_profile'),
    path('dashboard/admin/businesses/',views.pending_businesses_view,name='pending_businesses',),
    path('dashboard/admin/businesses/<int:business_id>/<str:action>/',views.update_business_verification,name='update_business_verification',),
]