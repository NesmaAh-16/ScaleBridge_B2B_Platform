from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from accounts.models import Business

class Category(models.Model):
    name = models.CharField(max_length=100) # Increased slightly
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = "Categories" 

class Product(models.Model):
    TYPE_CHOICES = [
        ('PRODUCT', 'Finished Product'),
        ('MATERIAL', 'Raw Material'),
    ]

    CURRENCY_CHOICES = [
        ('USD', 'USD'),
        ('EUR', 'EUR'),
        ('GBP', 'GBP'),
        ('JOD', 'JOD'),
        ('SAR', 'SAR'),
        ('AED', 'AED'),
        ('EGP', 'EGP'),
        ('TRY', 'TRY'),
    ]

    UNIT_CHOICES = [
        ('kg',  'kg'),
        ('g',   'g'),
        ('ton', 'ton'),
        ('lb',  'lb'),
        ('L',   'L'),
        ('m',   'm'),
        ('m²',  'm²'),
        ('m³',  'm³'),
        ('pcs', 'pcs'),
        ('box', 'box'),
        ('pallet', 'pallet'),
        ('unit', 'unit'),
    ]

    business = models.ForeignKey('accounts.Business', on_delete=models.CASCADE, related_name='products')
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    unit = models.CharField(max_length=45, choices=UNIT_CHOICES)
    price = models.DecimalField(max_digits=15, decimal_places=2)
    currency = models.CharField(max_length=3, choices=CURRENCY_CHOICES, default='USD')
    image = models.ImageField(upload_to='product_images/', null=True, blank=True)
    product_type = models.CharField(max_length=10, choices=TYPE_CHOICES)
    is_group_buy = models.BooleanField(default=False)
    min_order_quantity = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True, validators=[MinValueValidator(0)])
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} ({self.product_type})"
class BuyingCircle(models.Model):
    # Mapping ENUM('Open', 'Closed', 'Completed') 
    STATUS_CHOICES = [
        ('Open', 'Open'),
        ('Closed', 'Closed'),
        ('Completed', 'Completed'),
    ]
    
    created_by = models.ForeignKey('accounts.Business', on_delete=models.CASCADE, related_name='created_circles')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    target_quantity = models.DecimalField(max_digits=15, decimal_places=2)
    current_quantity = models.DecimalField(max_digits=15, decimal_places=2, default=0.00)
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='Open')
    deadline = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    @property
    def progress_percentage(self):
        if not self.target_quantity or self.target_quantity <= 0:
            return 0
        # Use float for the calculation to ensure precision
        percentage = (float(self.current_quantity) / float(self.target_quantity)) * 100
        # Return at least 0.1 if there is any quantity, or round to 1 decimal place
        if 0 < percentage < 1:
            return 0.1
        return min(round(percentage, 1), 100)
    @property
    def remaining_quantity(self):
        """Calculates the gap to target. Ensures we never return a negative number."""
        diff = self.target_quantity - self.current_quantity
        return max(diff, 0)
    
    @property
    def progress_label(self):
        return f"{self.current_quantity:,.0f} / {self.target_quantity:,.0f}"

    @property
    def is_reached(self):
        return self.current_quantity >= self.target_quantity
    
class BuyingCircleMember(models.Model):
    buying_circle = models.ForeignKey(BuyingCircle, on_delete=models.CASCADE, related_name='members')
    business = models.ForeignKey(Business, on_delete=models.CASCADE)
    requested_quantity = models.DecimalField(max_digits=15, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class Order(models.Model):
    # Mapping ENUM('Pending', 'Accepted', 'InProgress', 'Completed', 'CANCELLED') 
    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Accepted', 'Accepted'),
        ('InProgress', 'In Progress'),
        ('Completed', 'Completed'),
        ('CANCELLED', 'Cancelled'),
    ]
    
    # Optional relation to circle (buying_circle_id INT)
    buying_circle = models.ForeignKey(BuyingCircle, on_delete=models.SET_NULL, null=True, blank=True)
    buyer_business = models.ForeignKey('accounts.Business', on_delete=models.CASCADE, related_name='purchases')
    supplier_business = models.ForeignKey('accounts.Business', on_delete=models.CASCADE, related_name='sales')
    total_quantity = models.DecimalField(max_digits=15, decimal_places=2)
    price_at_purchase = models.DecimalField(max_digits=15, decimal_places=2)
    total_price = models.DecimalField(max_digits=15, decimal_places=2)
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='Pending')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        if self.buying_circle:
            return f"Bulk Order: {self.buying_circle.product.name} (Group Order)"
        return f"Direct Order: {self.id} - {self.buyer_business.business_name}"

class Review(models.Model):
    from_business = models.ForeignKey(Business, on_delete=models.CASCADE, related_name='reviews_given')
    to_business = models.ForeignKey(Business, on_delete=models.CASCADE, related_name='reviews_received')
    # Link to Order (order_id INT)
    order = models.OneToOneField(Order, on_delete=models.CASCADE)
    # Ensures the database ONLY accepts numbers between 1 and 5
    rating = models.IntegerField(
        validators=[
            MinValueValidator(1), 
            MaxValueValidator(5)
        ]
    )
    comment = models.CharField(max_length=255, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class Notification(models.Model):
    user = models.ForeignKey('accounts.User', on_delete=models.CASCADE, related_name='notifications')
    title = models.CharField(max_length=255)
    message = models.TextField()
    is_read = models.BooleanField(default=False) # is_read TINYINT
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.title} - {self.user.email}"
    
