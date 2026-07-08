from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from accounts.decorators import role_required
from accounts.models import Business
from .models import Product, Category, BuyingCircle, BuyingCircleMember, Order, Notification
from django.db.models import Q
from .models import Product, Category, BuyingCircle, BuyingCircleMember, Order
from .forms import ProductForm, BuyingCircleForm, JoinCircleForm
from django.db import transaction
from .forms import ProductForm, BuyingCircleForm, JoinCircleForm, ReviewForm
from django.db import transaction 
from .models import Notification 
from django.db.models import Q
from django.http import JsonResponse

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

    # DOCTOR'S EMERGENCY FIX: 
    # 1. We normalize the role to uppercase to avoid case-sensitivity errors.
    # 2. We check for both variations just in case.
    user_role = request.user.role.upper() if request.user.role else ""

    can_join = (
        business is not None  # Must have a profile
        and not is_member     # Must not be in already
        and circle.status == 'Open' 
        and business != circle.product.business  # Must not be the supplier
        and (user_role == 'SMALL_BUSINESS' or user_role == 'SMALLBUSINESS') 
    )

    join_form = JoinCircleForm() if can_join else None
    is_enterprise = user_role == 'ENTERPRISEBUYER'

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

    # ... (Keep your validation checks)

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
            
            # DOCTOR'S FIX: Only add as member if they aren't the supplier
            if business != product.business:
                BuyingCircleMember.objects.create(
                    buying_circle=circle,
                    business=business,
                    requested_quantity=requested_qty,
                )
            
            _maybe_close_circle(circle)
            return redirect('operations:circle_detail', pk=circle.pk)
def _maybe_close_circle(circle):
    if circle.status != 'Open' or circle.current_quantity < circle.target_quantity:
        return

    circle.status = 'Closed'
    circle.save()

    # Find a buyer who is NOT the supplier.
    customer_member = circle.members.exclude(business=circle.product.business).first()
    
    if customer_member:
        actual_buyer = customer_member.business
    else:
        actual_buyer = Business.objects.exclude(id=circle.product.business.id).first()

    # --- THE CRITICAL FIX IS THE NEXT LINE: Add 'new_order =' ---
    new_order = Order.objects.create(
        buying_circle=circle,
        buyer_business=actual_buyer,                
        supplier_business=circle.product.business,  
        total_quantity=circle.current_quantity,
        price_at_purchase=circle.product.price,
        total_price=circle.current_quantity * circle.product.price,
        status='Pending',
    )

    # Now 'new_order' exists, so the line below will NOT crash anymore!
    notification_list = []
    success_msg = f"Success! The Buying Circle for {circle.product.name} has reached its target. Order #{new_order.id} is now generated."
    
    # Notify all members
    for membership in circle.members.all():
        notification_list.append(
            Notification(
                user=membership.business.user,
                title="Circle Success!",
                message=success_msg
            )
        )
    
    # Notify the Supplier
    notification_list.append(
        Notification(
            user=circle.product.business.user,
            title="New Bulk Order Created",
            message=f"Your group listing for {circle.product.name} has closed. You have a new bulk order pending approval."
        )
    )

    Notification.objects.bulk_create(notification_list)

# --- 2. THE VIEW FUNCTION (THIS IS WHERE REQUEST AND PK LIVE) ---
@login_required
@role_required('SmallBusiness')
def circle_join(request, pk): # <--- 'request' and 'pk' are defined HERE
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




@login_required
def update_order_status(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    business = Business.objects.filter(user=request.user).first()

    # SECURITY: Only the Supplier can update the status
    if order.supplier_business != business:
        messages.error(request, "Access Denied: Unauthorized entity.")
        return redirect('accounts:business_dashboard')

    if request.method == 'POST':
        action = request.POST.get('action')
        old_status = order.status
        status_changed = False

        with transaction.atomic():
            # 1. LOGIC FOR 'ACCEPT'
            if action == 'accept' and order.status == 'Pending':
                order.status = 'Accepted'
                status_changed = True
                success_message = f"Order #{order.id} has been accepted. Processing started."

            # 2. LOGIC FOR 'START' (Dispatch)
            elif action == 'start' and order.status == 'Accepted':
                order.status = 'InProgress'
                status_changed = True
                success_message = f"Order #{order.id} is now being prepared for shipping."

            # 3. LOGIC FOR 'COMPLETE' (Finalize)
            elif action == 'complete' and order.status == 'InProgress':
                order.status = 'Completed'
                status_changed = True
                success_message = f"Order #{order.id} is complete."
                
                # Archiving the circle
                if order.buying_circle:
                    circle = order.buying_circle
                    circle.status = 'Completed'
                    circle.save()

                    # Success Loop: Start new iteration
                    _ensure_group_buy_circle(circle.product, order.supplier_business)

                    # Notify members to review
                    members = circle.members.all()
                    for member in members:
                        Notification.objects.create(
                            user=member.business.user,
                            title="Package Arrived!",
                            message = f"Order for {circle.product.name} is complete. Please leave a review!"
                        )

            # 4. LOGIC FOR 'CANCEL'
            elif action == 'cancel':
                order.status = 'CANCELLED'
                status_changed = True
                success_message = f"Order #SB-{order.id} has been terminated."

            # SAVE AND NOTIFY IF CHANGED
            if status_changed:
                order.save()
                
                # NOTIFICATION FOR THE BUYER
                Notification.objects.create(
                    user=order.buyer_business.user,
                    title="Order Status Updated",
                    message=f"Order #SB-{order.id} has been marked as {order.status}."
                )
                messages.success(request, success_message)
            else:
                messages.warning(request, "Invalid action or state transition for this order.")

    return redirect('accounts:business_dashboard')

# ---------------------------------------------------------------------------
# Trust Engine: Reputation & Review Gallery
# ---------------------------------------------------------------------------

def business_reviews(request, business_id):
    """
    The Public Trust Page: 
    Shows all reviews received by a business so buyers can verify their reliability.
    """
    target_business = get_object_or_404(Business, id=business_id)
    received_reviews = target_business.reviews_received.all().order_by('-created_at')
    
    return render(request, 'operations/business_reviews.html', {
        'target_business': target_business,
        'reviews': received_reviews,
    })

# ---------------------------------------------------------------------------
# Notification Console API (Required by base.html script)
# ---------------------------------------------------------------------------

from django.http import JsonResponse

@login_required
def notification_unread_count(request):
    """
    API Endpoint for the Polling Script:
    Returns the count of unread notifications for the user's dashboard.
    """
    count = Notification.objects.filter(user=request.user, is_read=False).count()
    return JsonResponse({'unread_count': count})

@login_required
def mark_notification_read(request, notification_id):
    """
    Action to clear a vanguard alert from the UI.
    """
    notification = get_object_or_404(Notification, id=notification_id, user=request.user)
    notification.is_read = True
    notification.save()
    
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({'status': 'success'})
        
    return redirect('accounts:business_dashboard')

# --- ADD THESE FUNCTIONS TO THE BOTTOM OF operations/views.py ---

@login_required
def order_detail(request, order_id):
    """
    The Detailed Ledger: Shows specific transaction data and participant info.
    """
    order = get_object_or_404(Order, id=order_id)
    business = Business.objects.filter(user=request.user).first()

    # Security: Only Buyer or Supplier can see this
    if business not in [order.buyer_business, order.supplier_business]:
        messages.error(request, "Access Denied: You are not part of this transaction.")
        return redirect('accounts:business_dashboard')

    review = getattr(order, 'review', None)
    
    return render(request, 'operations/order_detail.html', {
        'order': order,
        'business': business,
        'review': review
    })

@login_required
@transaction.atomic # Ensure database integrity
def leave_review(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    business = Business.objects.filter(user=request.user).first()

    # REQ: Validate order status is 'Completed'
    if order.status != 'Completed':
        messages.error(request, "Review portal opens only after order completion.")
        return redirect('operations:order_detail', order_id=order.id)

    # REQ: Ensure 1:1 relationship (prevent duplicates)
    if hasattr(order, 'review'):
        messages.warning(request, "This transaction has already been rated.")
        return redirect('operations:order_detail', order_id=order.id)

    if request.method == 'POST':
        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.order = order
            review.from_business = business
            review.to_business = order.supplier_business
            review.save()

            # REQ: Trigger update to average_rating column
            order.supplier_business.update_trust_score()

            messages.success(request, "Trust Score Updated. Feedback Committed.")
            return redirect('operations:order_detail', order_id=order.id)
    else:
        form = ReviewForm()

    return render(request, 'operations/review_form.html', {'form': form, 'order': order})

@login_required
def notification_unread_count(request):
    """
    API for the Vanguard Console: Returns unread alert count.
    """
    count = Notification.objects.filter(user=request.user, is_read=False).count()
    return JsonResponse({'unread_count': count})

@login_required
def order_ledger_view(request):
    business = Business.objects.filter(user=request.user).first()
    orders = Order.objects.filter(Q(buyer_business=business) | Q(supplier_business=business))
    return render(request, 'operations/order_ledger.html', {'orders': orders, 'business': business})

from django.http import HttpResponse
from django.template.loader import get_template
from xhtml2pdf import pisa 

@login_required
def order_pdf_view(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    business = Business.objects.filter(user=request.user).first()

    # SECURITY: Only Buyer or Supplier can generate this PDF
    if business not in [order.buyer_business, order.supplier_business]:
        return HttpResponse("Access Denied", status=401)

    template_path = 'operations/order_pdf_template.html'
    context = {'order': order, 'business': business}
    
    # Create a Django response object, and specify content_type as pdf
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="Invoice_SB_{order.id}.pdf"'
    
    # Render the template
    template = get_template(template_path)
    html = template.render(context)

    # Run the PDF conversion
    pisa_status = pisa.CreatePDF(html, dest=response)
    
    if pisa_status.err:
       return HttpResponse('Error generating PDF', status=500)
    return response