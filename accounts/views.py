from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import RegisterForm, LoginForm
from .models import User, Business
from .decorators import role_required
from django.utils.html import escape  
from django.db import DatabaseError


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
    return render(request, 'dashboard.html', {'business': business})


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