from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from accounts.decorators import role_required
from accounts.models import Business
from .models import Product, Category, BuyingCircle, BuyingCircleMember, Order
from .forms import ProductForm, BuyingCircleForm, JoinCircleForm
from django.db import transaction


# ---------------------------------------------------------------------------
# Product CRUD
# ---------------------------------------------------------------------------

def _ensure_group_buy_circle(product, business):
    """Auto-start an Open buying circle when demand aggregation is enabled."""
    if product.is_group_buy and product.min_order_quantity:
        if not BuyingCircle.objects.filter(product=product, status='Open').exists():
            BuyingCircle.objects.create(
                created_by=business,
                product=product,
                target_quantity=product.min_order_quantity,
            )

@login_required
@role_required('SmallBusiness', 'EnterpriseBuyer')
def product_list(request):
    business = Business.objects.filter(user=request.user).first()
    products = Product.objects.filter(business=business)

    is_enterprise = request.user.role == 'EnterpriseBuyer'
    fixed_product_type_label = 'Raw Material' if is_enterprise else 'Finished Product'

    return render(request, 'operations/product_list.html', {
        'products': products,
        'catalog_title': f'My {fixed_product_type_label} Catalog',
        'add_button_label': f'Add New {fixed_product_type_label}',
    })


@login_required
@role_required('SmallBusiness', 'EnterpriseBuyer')
def product_create(request):
    business = Business.objects.filter(user=request.user).first()

    if not business:
        messages.error(request, 'You need to complete your business profile before adding products.')
        return redirect('accounts:business_profile')

    is_enterprise = request.user.role == 'EnterpriseBuyer'
    fixed_product_type = 'MATERIAL' if is_enterprise else 'PRODUCT'
    fixed_product_type_label = 'Raw Material' if is_enterprise else 'Finished Product'
    title = f'Add New {fixed_product_type_label}'

    if request.method == 'POST':
        form = ProductForm(request.POST, fixed_product_type=fixed_product_type, allow_group_buy=is_enterprise)
        if form.is_valid():
            product = form.save(commit=False)
            product.business = business
            product.save()
            _ensure_group_buy_circle(product, business)
            messages.success(request, f'Item "{product.name}" added successfully!')
            return redirect('operations:product_list')
    else:
        form = ProductForm(fixed_product_type=fixed_product_type, allow_group_buy=is_enterprise)

    return render(request, 'operations/product_form.html', {
        'form': form,
        'title': title,
        'fixed_product_type': fixed_product_type,
        'fixed_product_type_label': fixed_product_type_label,
    })


@login_required
@role_required('SmallBusiness', 'EnterpriseBuyer')
def product_update(request, pk):
    product = get_object_or_404(Product, pk=pk, business__user=request.user)
    is_enterprise = request.user.role == 'EnterpriseBuyer'

    if request.method == 'POST':
        form = ProductForm(request.POST, instance=product, allow_group_buy=is_enterprise)
        if form.is_valid():
            product = form.save()
            _ensure_group_buy_circle(product, product.business)
            messages.success(request, f'"{product.name}" updated successfully!')
            return redirect('operations:product_list')
    else:
        form = ProductForm(instance=product, allow_group_buy=is_enterprise)

    return render(request, 'operations/product_form.html', {'form': form, 'title': 'Edit Item'})


@login_required
@role_required('SmallBusiness', 'EnterpriseBuyer')
def product_delete(request, pk):
    product = get_object_or_404(Product, pk=pk, business__user=request.user)
    if request.method == 'POST':
        product.delete()
        messages.success(request, "Item removed from your catalog.")
        return redirect('operations:product_list')
    return render(request, 'operations/product_confirm_delete.html', {'product': product})


# ---------------------------------------------------------------------------
# Marketplace
# ---------------------------------------------------------------------------

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

    group_buy = request.GET.get('group_buy')
    if group_buy:
        products = products.filter(is_group_buy=True)

    categories = Category.objects.all()

    # Build maps: open circles and closed/completed circles per product
    all_circles = BuyingCircle.objects.filter(
        product__in=products, status__in=('Open', 'Closed', 'Completed')
    ).select_related('product').order_by('-created_at')

    open_circle_map = {}
    closed_circle_map = {}
    for c in all_circles:
        if c.status == 'Open' and c.product_id not in open_circle_map:
            open_circle_map[c.product_id] = c
        elif c.status in ('Closed', 'Completed') and c.product_id not in closed_circle_map:
            closed_circle_map[c.product_id] = c

    products_with_circles = []
    for p in products:
        products_with_circles.append({
            'product': p,
            'open_circle': open_circle_map.get(p.pk),
            'closed_circle': closed_circle_map.get(p.pk),
        })

    is_enterprise = request.user.is_authenticated and request.user.role == 'EnterpriseBuyer'

    member_circle_ids = set()
    if request.user.is_authenticated:
        business = Business.objects.filter(user=request.user).first()
        if business:
            member_circle_ids = set(
                BuyingCircleMember.objects.filter(business=business)
                .values_list('buying_circle_id', flat=True)
            )

    context = {
        'products_with_circles': products_with_circles,
        'categories': categories,
        'current_category': category_id,
        'current_type': p_type,
        'query': query,
        'group_buy_filter': group_buy,
        'is_enterprise': is_enterprise,
        'member_circle_ids': member_circle_ids,
    }
    return render(request, 'operations/marketplace_list.html', context)


# ---------------------------------------------------------------------------
# Buying Circles — list
# ---------------------------------------------------------------------------

def buying_circle_list(request):
    status_filter = request.GET.get('status', '')
    qs = BuyingCircle.objects.select_related('product', 'created_by').all()
    if status_filter in ('Open', 'Closed', 'Completed'):
        qs = qs.filter(status=status_filter)

    # Track which circles the current user's business is already in
    member_circle_ids = set()
    if request.user.is_authenticated:
        business = Business.objects.filter(user=request.user).first()
        if business:
            member_circle_ids = set(
                BuyingCircleMember.objects.filter(business=business)
                .values_list('buying_circle_id', flat=True)
            )

    status_tabs = [
        ('All', ''),
        ('Open', 'Open'),
        ('Closed', 'Closed'),
        ('Completed', 'Completed'),
    ]

    is_enterprise = request.user.is_authenticated and request.user.role == 'EnterpriseBuyer'

    return render(request, 'operations/buying_circle_list.html', {
        'buying_circles': qs,
        'status_filter': status_filter,
        'member_circle_ids': member_circle_ids,
        'status_tabs': status_tabs,
        'is_enterprise': is_enterprise,
    })


# ---------------------------------------------------------------------------
# Buying Circles — detail, create, join, leave
# ---------------------------------------------------------------------------

@login_required
def circle_detail(request, pk):
    circle = get_object_or_404(BuyingCircle, pk=pk)
    members = circle.members.select_related('business').order_by('created_at')

    business = Business.objects.filter(user=request.user).first()
    user_membership = members.filter(business=business).first() if business else None
    is_member = user_membership is not None
    can_join = (
        business is not None
        and not is_member
        and circle.status == 'Open'
        and business != circle.product.business  # supplier can't join their own circle
        and request.user.role != 'EnterpriseBuyer'  # enterprises don't buy raw materials via circles
    )

    join_form = JoinCircleForm() if can_join else None
    is_enterprise = request.user.role == 'EnterpriseBuyer'

    context = {
        'circle': circle,
        'members': members,
        'is_member': is_member,
        'user_membership': user_membership,
        'can_join': can_join,
        'join_form': join_form,
        'is_enterprise': is_enterprise,
    }
    return render(request, 'operations/circle_detail.html', context)


@login_required
@role_required('SmallBusiness')
def circle_create(request, product_pk):
    product = get_object_or_404(Product, pk=product_pk, is_group_buy=True)
    business = Business.objects.filter(user=request.user).first()

    if not business:
        messages.error(request, 'Complete your business profile first.')
        return redirect('accounts:business_profile')

    # Redirect to existing open circle if one already exists for this product
    existing = BuyingCircle.objects.filter(product=product, status='Open').first()
    if existing:
        messages.info(request, f'A circle for {product.name} is already open — you can join it.')
        return redirect('operations:circle_detail', pk=existing.pk)

    if not product.min_order_quantity:
        messages.error(request, 'This product has no minimum order quantity set. Contact the supplier.')
        return redirect('operations:marketplace')

    if request.method == 'POST':
        form = BuyingCircleForm(request.POST)
        if form.is_valid():
            requested_qty = form.cleaned_data['requested_quantity']

            circle = BuyingCircle.objects.create(
                created_by=business,
                product=product,
                target_quantity=product.min_order_quantity,
                current_quantity=requested_qty,
            )
            BuyingCircleMember.objects.create(
                buying_circle=circle,
                business=business,
                requested_quantity=requested_qty,
            )
            _maybe_close_circle(circle)
            messages.success(request, f'Buying circle started for {product.name}!')
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
    if request.method != 'POST':
        return redirect('operations:circle_detail', pk=pk)

    form = JoinCircleForm(request.POST)
    if not form.is_valid():
        messages.error(request, 'Invalid quantity. Please try again.')
        return redirect('operations:circle_detail', pk=pk)

    requested_qty = form.cleaned_data['requested_quantity']

    try:
        with transaction.atomic():
            circle = get_object_or_404(BuyingCircle.objects.select_for_update(), pk=pk, status='Open')
            business = Business.objects.filter(user=request.user).first()

            if not business:
                messages.error(request, 'Complete your business profile first.')
                return redirect('accounts:business_profile')

            if circle.members.filter(business=business).exists():
                messages.warning(request, 'You are already a member of this circle.')
                return redirect('operations:circle_detail', pk=pk)

            BuyingCircleMember.objects.create(
                buying_circle=circle,
                business=business,
                requested_quantity=requested_qty,
            )

            circle.current_quantity += requested_qty
            circle.save()

            _maybe_close_circle(circle)

        messages.success(request, f'You joined the buying circle for {circle.product.name}!')

    except BuyingCircle.DoesNotExist:
        messages.error(request, 'This buying circle is no longer available.')

    return redirect('operations:circle_detail', pk=pk)


@login_required
@role_required('SmallBusiness')
def circle_leave(request, pk):
    if request.method != 'POST':
        return redirect('operations:circle_detail', pk=pk)

    circle = get_object_or_404(BuyingCircle, pk=pk, status='Open')
    business = Business.objects.filter(user=request.user).first()
    membership = get_object_or_404(BuyingCircleMember, buying_circle=circle, business=business)

    circle.current_quantity = max(circle.current_quantity - membership.requested_quantity, 0)
    circle.save()
    membership.delete()

    messages.success(request, 'You have left the buying circle.')
    return redirect('operations:circle_detail', pk=pk)


# ---------------------------------------------------------------------------
# Internal helper
# ---------------------------------------------------------------------------

def _maybe_close_circle(circle):
    """Auto-close the circle and generate a consolidated order when target is met."""
    if circle.status != 'Open':
        return
    if circle.current_quantity < circle.target_quantity:
        return

    circle.status = 'Closed'
    circle.save()

    Order.objects.create(
        buying_circle=circle,
        buyer_business=circle.created_by,
        supplier_business=circle.product.business,
        total_quantity=circle.current_quantity,
        price_at_purchase=circle.product.price,
        total_price=circle.current_quantity * circle.product.price,
        status='Pending',
    )
