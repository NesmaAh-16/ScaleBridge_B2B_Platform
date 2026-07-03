from decimal import Decimal

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from accounts.decorators import role_required
from accounts.models import Business
from .models import Product, Category, BuyingCircle, BuyingCircleMember
from .forms import ProductForm, BuyingCircleForm, JoinCircleForm


@login_required
@role_required('SmallBusiness', 'EnterpriseBuyer')
def product_list(request):
    business = Business.objects.filter(user=request.user).first()
    products = Product.objects.filter(business=business)
    return render(request, 'operations/product_list.html', {'products': products})


@login_required
@role_required('SmallBusiness')
def product_create(request):
    business = Business.objects.filter(user=request.user).first()

    if request.method == 'POST':
        form = ProductForm(request.POST)
        if form.is_valid():
            product = form.save(commit=False)
            product.business = business
            product.save()
            messages.success(request, f'Item "{product.name}" added successfully!')
            return redirect('operations:product_list')
    else:
        form = ProductForm()

    return render(request, 'operations/product_form.html', {'form': form, 'title': 'Add New Item'})


@login_required
@role_required('SmallBusiness')
def product_update(request, pk):
    product = get_object_or_404(Product, pk=pk, business__user=request.user)

    if request.method == 'POST':
        form = ProductForm(request.POST, instance=product)
        if form.is_valid():
            form.save()
            messages.success(request, f'"{product.name}" updated successfully!')
            return redirect('operations:product_list')
    else:
        form = ProductForm(instance=product)

    return render(request, 'operations/product_form.html', {'form': form, 'title': 'Edit Item'})


@login_required
@role_required('SmallBusiness')
def product_delete(request, pk):
    product = get_object_or_404(Product, pk=pk, business__user=request.user)
    if request.method == 'POST':
        product.delete()
        messages.success(request, "Item removed from your catalog.")
        return redirect('operations:product_list')
    return render(request, 'operations/product_confirm_delete.html', {'product': product})


def marketplace_list(request):
    products = Product.objects.all().select_related('category', 'business')

    query = request.GET.get('q')
    if query:
        products = products.filter(name__icontains=query)

    category_id = request.GET.get('category')
    if category_id:
        products = products.filter(category_id=category_id)

    p_type = request.GET.get('type')
    if p_type:
        products = products.filter(product_type=p_type)

    categories = Category.objects.all()

    context = {
        'products': products,
        'categories': categories,
        'current_category': category_id,
        'current_type': p_type,
        'query': query,
    }
    return render(request, 'operations/marketplace_list.html', context)


def buying_circle_list(request):
    buying_circles = BuyingCircle.objects.select_related(
        'product',
        'created_by'
    ).all()

    status_filter = request.GET.get('status', '')
    if status_filter in ['Open', 'Closed', 'Completed']:
        buying_circles = buying_circles.filter(status=status_filter)

    business = None
    member_circle_ids = set()
    is_enterprise = False

    if request.user.is_authenticated:
        business = Business.objects.filter(user=request.user).first()
        is_enterprise = request.user.role == 'EnterpriseBuyer'

    if business:
        member_circle_ids = set(
            BuyingCircleMember.objects.filter(business=business)
            .values_list('buying_circle_id', flat=True)
        )

    return render(request, 'operations/buying_circle_list.html', {
        'buying_circles': buying_circles,
        'status_tabs': [
            ('All', ''),
            ('Open', 'Open'),
            ('Closed', 'Closed'),
            ('Completed', 'Completed'),
        ],
        'status_filter': status_filter,
        'member_circle_ids': member_circle_ids,
        'is_enterprise': is_enterprise,
    })


def circle_detail(request, pk):
    circle = get_object_or_404(
        BuyingCircle.objects.select_related('product', 'product__business', 'created_by'),
        pk=pk,
    )
    members = circle.members.select_related('business').all()

    business = None
    user_membership = None
    is_member = False
    can_join = False
    is_enterprise = False

    if request.user.is_authenticated:
        business = Business.objects.filter(user=request.user).first()
        is_enterprise = request.user.role == 'EnterpriseBuyer'

    if business:
        user_membership = members.filter(business=business).first()
        is_member = user_membership is not None
        can_join = (
            request.user.role == 'SmallBusiness'
            and circle.status == 'Open'
            and not is_member
        )

    return render(request, 'operations/circle_detail.html', {
        'circle': circle,
        'members': members,
        'join_form': JoinCircleForm(),
        'is_enterprise': is_enterprise,
        'is_member': is_member,
        'user_membership': user_membership,
        'can_join': can_join,
    })


@login_required
@role_required('SmallBusiness')
def circle_create(request, product_pk):
    product = get_object_or_404(Product, pk=product_pk, is_group_buy=True)
    business = Business.objects.filter(user=request.user).first()

    if not business:
        messages.error(request, 'Create your business profile before starting a buying circle.')
        return redirect('operations:marketplace')

    if request.method == 'POST':
        form = BuyingCircleForm(request.POST)
        if form.is_valid():
            requested_quantity = form.cleaned_data['requested_quantity']
            target_quantity = product.min_order_quantity or requested_quantity
            status = 'Closed' if requested_quantity >= target_quantity else 'Open'

            circle = BuyingCircle.objects.create(
                created_by=business,
                product=product,
                target_quantity=target_quantity,
                current_quantity=requested_quantity,
                status=status,
            )
            BuyingCircleMember.objects.create(
                buying_circle=circle,
                business=business,
                requested_quantity=requested_quantity,
            )
            messages.success(request, 'Buying circle started successfully.')
            return redirect('operations:circle_detail', pk=circle.pk)
    else:
        form = BuyingCircleForm()

    return render(request, 'operations/circle_create.html', {
        'form': form,
        'product': product,
    })


@login_required
@role_required('SmallBusiness')
def circle_join(request, pk):
    circle = get_object_or_404(BuyingCircle, pk=pk, status='Open')
    business = Business.objects.filter(user=request.user).first()

    if not business:
        messages.error(request, 'Create your business profile before joining a buying circle.')
        return redirect('operations:circle_detail', pk=circle.pk)

    if BuyingCircleMember.objects.filter(buying_circle=circle, business=business).exists():
        messages.warning(request, 'You are already a member of this buying circle.')
        return redirect('operations:circle_detail', pk=circle.pk)

    if request.method == 'POST':
        form = JoinCircleForm(request.POST)
        if form.is_valid():
            requested_quantity = form.cleaned_data['requested_quantity']
            BuyingCircleMember.objects.create(
                buying_circle=circle,
                business=business,
                requested_quantity=requested_quantity,
            )

            circle.current_quantity += requested_quantity
            if circle.current_quantity >= circle.target_quantity:
                circle.status = 'Closed'
            circle.save(update_fields=['current_quantity', 'status', 'updated_at'])

            messages.success(request, 'You joined the buying circle successfully.')

    return redirect('operations:circle_detail', pk=circle.pk)


@login_required
@role_required('SmallBusiness')
def circle_leave(request, pk):
    circle = get_object_or_404(BuyingCircle, pk=pk)
    business = Business.objects.filter(user=request.user).first()

    if not business:
        messages.error(request, 'Business profile not found.')
        return redirect('operations:circle_detail', pk=circle.pk)

    membership = get_object_or_404(BuyingCircleMember, buying_circle=circle, business=business)

    if circle.status != 'Open':
        messages.error(request, 'Closed buying circles cannot be changed.')
        return redirect('operations:circle_detail', pk=circle.pk)

    circle.current_quantity = max(
        Decimal('0'),
        circle.current_quantity - membership.requested_quantity,
    )
    circle.save(update_fields=['current_quantity', 'updated_at'])
    membership.delete()

    messages.success(request, 'You left the buying circle.')
    return redirect('operations:circle_detail', pk=circle.pk)
