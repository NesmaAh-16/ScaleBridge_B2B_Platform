from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import RegisterForm, LoginForm
from .models import User, Business
from .decorators import role_required
from django.utils.html import escape  
from django.db import DatabaseError
from operations.models import BuyingCircle
from django.db.models import Q
from operations.models import Order, Notification


def register_view(request):
    if request.user.is_authenticated:
        return redirect('accounts:dashboard')

    form = RegisterForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        user = form.save()
        login(request, user)
        messages.success(request, f'Welcome to ScaleBridge, {user.first_name}!')
        return redirect('accounts:dashboard')

    return render(request, 'accounts/register.html', {'form': form})


def login_view(request):
    if request.user.is_authenticated:
        return redirect('accounts:dashboard')

    form = LoginForm(request, data=request.POST or None)
    if request.method == 'POST' and form.is_valid():
        user = form.get_user()
        login(request, user)
        messages.success(request, f'Welcome back, {user.first_name or user.email}!')
        return redirect('accounts:dashboard')

    return render(request, 'accounts/login.html', {'form': form})


def logout_view(request):
    if request.method == 'POST':
        logout(request)
    return redirect('accounts:login')


@login_required
def profile_view(request):
    return render(request, 'accounts/profile.html')


@login_required
def dashboard_view(request):
    if request.user.is_superuser or request.user.role == 'Admin':
        return redirect('accounts:admin_dashboard')
    if request.user.role in ('SmallBusiness', 'EnterpriseBuyer'):
        return redirect('accounts:business_dashboard')
    return redirect('accounts:profile')


@login_required
@role_required('Admin')
def admin_dashboard_view(request):
    total_users = User.objects.count()
    total_businesses = Business.objects.count()
    pending_businesses = Business.objects.filter(verification_status='pending').count()
    active_businesses = Business.objects.filter(verification_status='approved').count()
    return render(request, 'accounts/admin_dashboard.html', {
        'total_users': total_users,
        'total_businesses': total_businesses,
        'pending_businesses': pending_businesses,
        'active_businesses': active_businesses,
    })


@login_required
@role_required('SmallBusiness', 'EnterpriseBuyer')
def business_dashboard_view(request):
    business = Business.objects.filter(user=request.user).first()

    buying_circles = BuyingCircle.objects.select_related('product','created_by').all()

    return render(request, 'dashboard.html', {
        'business': business,
        'buying_circles': buying_circles})


@login_required
def business_profile(request):
    business = Business.objects.filter(user=request.user).first()

    if request.method == 'POST':
        # Use escape() to turn <script> into &lt;script&gt;
        business_name = escape(request.POST.get('business_name', '').strip())
        location = escape(request.POST.get('location', '').strip())
        business_type = request.POST.get('business_type', '').strip()
        description = escape(request.POST.get('description', '').strip())

        if not business_name or not location or not business_type:
            messages.error(request, 'Please fill in all required fields.')
            return redirect('accounts:business_profile')

        if business:
            business.business_name = business_name
            business.location = location
            business.business_type = business_type
            business.description = description
            business.save()
            messages.success(request, 'Business profile updated successfully.')
        else:
            Business.objects.create(
                user=request.user,
                business_name=business_name,
                location=location,
                business_type=business_type,
                description=description,
                verification_status='pending'
            )
            messages.success(request, 'Business profile saved successfully.')

        return redirect('accounts:business_profile')

    return render(request, 'accounts/business_profile.html', {
        'business': business
    })

@login_required
def business_profile(request):
    business = Business.objects.filter(user=request.user).first()

    if request.method == 'POST':
        business_name = escape(request.POST.get('business_name', '').strip())
        location = escape(request.POST.get('location', '').strip())
        business_type = request.POST.get('business_type', '').strip()
        description = escape(request.POST.get('description', '').strip())

        if not business_name or not location or not business_type:
            messages.error(request, 'Please fill in all required fields.')
            return redirect('accounts:business_profile')

        # Wrap the database operations in a try block
        try:
            if business:
                business.business_name = business_name
                business.location = location
                business.business_type = business_type
                business.description = description
                business.save() # The ORM handles SQL injection protection here
                messages.success(request, 'Business profile updated successfully.')
            else:
                Business.objects.create(
                    user=request.user,
                    business_name=business_name,
                    location=location,
                    business_type=business_type,
                    description=description,
                    verification_status='pending'
                )
                messages.success(request, 'Business profile saved successfully.')
        
        # The Safety Net for SQL/Database integrity errors
        except DatabaseError:
            messages.error(request, 'A database error occurred. Your input may contain invalid characters.')
            return redirect('accounts:business_profile')

        return redirect('accounts:business_profile')

    return render(request, 'accounts/business_profile.html', {
        'business': business
    })

@login_required
@role_required('SmallBusiness', 'EnterpriseBuyer')
def business_dashboard_view(request):
    # Identify the business
    business = Business.objects.filter(user=request.user).first()

    # 1. Get filtered circles
    buying_circles = BuyingCircle.objects.filter(
        Q(members__business=business) | Q(created_by=business)
    ).select_related('product','created_by').distinct()

    # 2. Get the 4 orders we found in the shell
    orders = Order.objects.filter(
        Q(buyer_business=business) | Q(supplier_business=business)
    ).select_related('buyer_business', 'supplier_business', 'buying_circle__product').order_by('-created_at')

    # --- THE MEDICAL MONITOR (Check your terminal after refreshing!) ---
    print(f"--- DASHBOARD DEBUG: Found {orders.count()} orders for {request.user.email} ---")

    # 3. Get Notifications
    notifications = Notification.objects.filter(user=request.user).order_by('-created_at')
    unread_count = notifications.filter(is_read=False).count()

    # 4. SEND TO HTML (Check that 'orders' is spelled correctly!)
    return render(request, 'dashboard.html', {
        'business': business,
        'buying_circles': buying_circles,
        'orders': orders,           # <--- This must match the {% for order in orders %}
        'notifications': notifications,
        'unread_count': unread_count,
    })

from django.contrib.auth import views as auth_views
from django.urls import reverse_lazy
from django.contrib import messages

class ScaleBridgePasswordResetView(auth_views.PasswordResetView):
    template_name = 'accounts/password_reset_form.html'
    email_template_name = 'accounts/password_reset_email.html'
    subject_template_name = 'accounts/password_reset_subject.txt'
    success_url = reverse_lazy('accounts:password_reset_done')

    def form_valid(self, form):
        # Professional Touch: Log that a reset was requested (helpful for debugging)
        opts = {
            'use_https': self.request.is_secure(),
            'token_generator': self.token_generator,
            'from_email': self.from_email,
            'email_template_name': self.email_template_name,
            'subject_template_name': self.subject_template_name,
            'request': self.request,
            'html_email_template_name': 'accounts/password_reset_email_html.html', # Send professional HTML email
        }
        form.save(**opts)
        messages.info(self.request, "If an account exists with that email, a reset link has been sent.")
        return super().form_valid(form)