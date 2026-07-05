from django.urls import path
from django.contrib.auth import views as auth_views
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
    
   # accounts/urls.py

path('password-reset/', 
    auth_views.PasswordResetView.as_view(
        template_name='accounts/password_reset_form.html',
        # This is for the plain text fallback (required)
        email_template_name='accounts/password_reset_email.html', 
        # This is for your beautiful HTML version
        html_email_template_name='accounts/password_reset_email.html', 
        success_url='/accounts/password-reset/done/'
    ),
    name='password_reset'),
        
    path('password-reset/done/', 
        auth_views.PasswordResetDoneView.as_view(template_name='accounts/password_reset_done.html'),
        name='password_reset_done'),
        
    path('password-reset-complete/', 
        auth_views.PasswordResetCompleteView.as_view(template_name='accounts/password_reset_complete.html'),
        name='password_reset_complete'),
    
    path('password-reset-confirm/<uidb64>/<token>/', 
    auth_views.PasswordResetConfirmView.as_view(
        template_name='accounts/password_reset_confirm.html',
        success_url='/accounts/password-reset-complete/' # <--- ADD THIS LINE
    ),
    name='password_reset_confirm'),
]