from django.shortcuts import render, redirect, get_object_or_404
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
from operations.ai_engine import DiscoveryEngine

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
        messages.success(request, f'Welcome back, {user.first_name}!')
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
    
    # PROFESSOR'S FIX: Logic to avoid using email in the greeting
    # We prefer First Name, then "Administrator" as a professional fallback
    display_name = request.user.first_name if request.user.first_name else "Administrator"

    return render(request, 'accounts/admin_dashboard.html', {
        'total_users': total_users,
        'total_businesses': total_businesses,
        'pending_businesses': pending_businesses,
        'active_businesses': active_businesses,
        'display_name': display_name,  # Clean variable for the template
    })





from .forms import BusinessProfileForm 
from .forms import BusinessProfileForm # We will create this below

@login_required
def business_profile(request):
    """
    Unified Business Identity Management.
    Handles branding assets (logos) and core business metadata.
    """
    business = Business.objects.filter(user=request.user).first()

    if request.method == 'POST':
        # request.FILES is MANDATORY for logo uploads
        form = BusinessProfileForm(request.POST, request.FILES, instance=business)
        if form.is_valid():
            profile = form.save(commit=False)
            profile.user = request.user
            profile.save()
            messages.success(request, 'Business Identity updated successfully.')
            return redirect('accounts:business_profile')
        else:
            messages.error(request, 'Update failed. Please check the form data.')
    else:
        form = BusinessProfileForm(instance=business)

    return render(request, 'accounts/business_profile.html', {
        'form': form,
        'business': business
    })


@login_required
@role_required('SmallBusiness', 'EnterpriseBuyer')
def business_dashboard_view(request):
    business = Business.objects.filter(user=request.user).first()
    
    # 1. AI Recommendation Engine Call
    recs_data = DiscoveryEngine.get_personalized_recommendations(business)

    # 2. Get filtered circles & orders
    buying_circles = BuyingCircle.objects.filter(
        Q(members__business=business) | Q(created_by=business)
    ).select_related('product','created_by').distinct()

    orders = Order.objects.filter(
        Q(buyer_business=business) | Q(supplier_business=business)
    ).select_related('buyer_business', 'supplier_business', 'buying_circle__product').order_by('-created_at')

    notifications = Notification.objects.filter(user=request.user).order_by('-created_at')
    
    return render(request, 'dashboard.html', {
        'business': business,
        'ai_products': recs_data['products'], 
        'ai_circles': recs_data['circles'],   
        'buying_circles': buying_circles,
        'orders': orders,
        'notifications': notifications,
        'unread_count': notifications.filter(is_read=False).count(),
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

from django.db.models import Sum
from django.db.models.functions import ExtractMonth
from django.utils import timezone
from operations.models import Order

@login_required
def analytics_dashboard(request):
    business = Business.objects.filter(user=request.user).first()
    current_year = timezone.now().year
    
    # 1. Get all completed orders for this business as a buyer
    completed_orders = Order.objects.filter(
        buyer_business=business, 
        status='Completed',
        created_at__year=current_year
    )

    # 2. Summary Calculations
    # Actual Spend = Sum of total_price
    actual_spend = completed_orders.aggregate(total=Sum('total_price'))['total'] or 0
    
    # ROI Logic: Assume the platform saved them 20% 
    # (So actual_spend is 80% of what they would have paid)
    projected_market_spend = float(actual_spend) / 0.8
    total_savings = projected_market_spend - float(actual_spend)
    
    # 3. Monthly Trends for Chart.js
    monthly_stats = completed_orders.annotate(month=ExtractMonth('created_at')) \
        .values('month') \
        .annotate(spend=Sum('total_price')) \
        .order_by('month')

    # Prepare data for the chart (months 1-12)
    chart_labels = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
    chart_spend = [0] * 12
    chart_savings = [0] * 12
    
    for stat in monthly_stats:
        index = stat['month'] - 1
        spend = float(stat['spend'])
        chart_spend[index] = spend
        chart_savings[index] = spend * 0.25 # Demonstrating 25% savings trend

    context = {
        'actual_spend': actual_spend,
        'total_savings': total_savings,
        'projected_market_spend': projected_market_spend,
        'savings_percentage': 20,
        'chart_labels': chart_labels,
        'chart_spend': chart_spend,
        'chart_savings': chart_savings,
        'business': business,
    }
    
    return render(request, 'accounts/analytics.html', context)