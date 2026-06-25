from django.db import models
from accounts.models import User, Business

class Category(models.Model):
    name = models.CharField(max_length=45)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class Product(models.Model):
    # Mapping ENUM('PRODUCT', 'MATERIAL') from Image 1
    TYPE_CHOICES = [
        ('PRODUCT', 'Product'),
        ('MATERIAL', 'Material'),
    ]
    
    business = models.ForeignKey(Business, on_delete=models.CASCADE, related_name='products')
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True)
    name = models.CharField(max_length=45)
    description = models.TextField(blank=True, null=True)
    unit = models.CharField(max_length=45)
    price = models.DecimalField(max_digits=15, decimal_places=2)
    
    # TINYINT maps to BooleanField
    product_type = models.CharField(max_length=10, choices=TYPE_CHOICES)
    is_group_buy = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class BuyingCircle(models.Model):
    # Mapping ENUM('Open', 'Closed', 'Completed') from Image 2
    STATUS_CHOICES = [
        ('Open', 'Open'),
        ('Closed', 'Closed'),
        ('Completed', 'Completed'),
    ]
    
    created_by = models.ForeignKey(Business, on_delete=models.CASCADE, related_name='created_circles')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    target_quantity = models.DecimalField(max_digits=15, decimal_places=2)
    current_quantity = models.DecimalField(max_digits=15, decimal_places=2, default=0.00)
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='Open')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class BuyingCircleMember(models.Model):
    buying_circle = models.ForeignKey(BuyingCircle, on_delete=models.CASCADE, related_name='members')
    business = models.ForeignKey(Business, on_delete=models.CASCADE)
    requested_quantity = models.DecimalField(max_digits=15, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class Order(models.Model):
    # Mapping ENUM('Pending', 'Accepted', 'InProgress', 'Completed', 'CANCELLED') from Image 4
    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Accepted', 'Accepted'),
        ('InProgress', 'In Progress'),
        ('Completed', 'Completed'),
        ('CANCELLED', 'Cancelled'),
    ]
    
    # Optional relation to circle (buying_circle_id INT)
    buying_circle = models.ForeignKey(BuyingCircle, on_delete=models.SET_NULL, null=True, blank=True)
    buyer_business = models.ForeignKey(Business, on_delete=models.CASCADE, related_name='purchases')
    supplier_business = models.ForeignKey(Business, on_delete=models.CASCADE, related_name='sales')
    
    total_quantity = models.DecimalField(max_digits=15, decimal_places=2)
    price_at_purchase = models.DecimalField(max_digits=15, decimal_places=2)
    total_price = models.DecimalField(max_digits=15, decimal_places=2)
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='Pending')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class Review(models.Model):
    from_business = models.ForeignKey(Business, on_delete=models.CASCADE, related_name='reviews_given')
    to_business = models.ForeignKey(Business, on_delete=models.CASCADE, related_name='reviews_received')
    # Link to Order (order_id INT)
    order = models.OneToOneField(Order, on_delete=models.CASCADE)
    rating = models.IntegerField()
    comment = models.CharField(max_length=255, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class Notification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    title = models.CharField(max_length=255)
    message = models.TextField()
    is_read = models.BooleanField(default=False) # is_read TINYINT
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)