from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from accounts.decorators import role_required
from accounts.models import Business
from .models import Product, Category, BuyingCircle
from .forms import ProductForm


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

    return render(request, 'operations/buying_circle_list.html', {
        'buying_circles': buying_circles
    })
