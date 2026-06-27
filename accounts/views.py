from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import RegisterForm, LoginForm
from .models import Business


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
    return render(request, 'dashboard.html')


@login_required
def business_profile(request):
    business = Business.objects.filter(user=request.user).first()

    if request.method == 'POST':
        business_name = request.POST.get('business_name', '').strip()
        location = request.POST.get('location', '').strip()
        business_type = request.POST.get('business_type', '').strip()
        description = request.POST.get('description', '').strip()

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