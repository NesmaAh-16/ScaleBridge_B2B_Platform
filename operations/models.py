from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from accounts.models import User, Business

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
    
    business = models.ForeignKey(Business, on_delete=models.CASCADE, related_name='products')
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True)
    name = models.CharField(max_length=255) # Increased to 255 for B2B details
    description = models.TextField(blank=True, null=True)
    unit = models.CharField(max_length=45, help_text="e.g. kg, ton, unit")
    price = models.DecimalField(max_digits=15, decimal_places=2) # 15 digits is great for high-value B2B
    
    product_type = models.CharField(max_length=10, choices=TYPE_CHOICES)
    is_group_buy = models.BooleanField(default=False)
    
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
    
    created_by = models.ForeignKey(Business, on_delete=models.CASCADE, related_name='created_circles')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    target_quantity = models.DecimalField(max_digits=15, decimal_places=2)
    current_quantity = models.DecimalField(max_digits=15, decimal_places=2, default=0.00)
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='Open')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    @property
    def progress_percentage(self):
        """Calculates 0-100 percentage for the progress bar"""
        if self.target_quantity > 0:
            percent = (self.current_quantity / self.target_quantity) * 100
            # Cap at 100 for the visual bar width, but keep as float for accuracy
            return min(round(float(percent), 1), 100.0)
        return 0

    @property
    def progress_label(self):
        """Returns the numerical ratio for the UI label"""
        return f"{self.current_quantity:,.0f} / {self.target_quantity:,.0f}"

    @property
    def is_reached(self):
        """Returns True if the goal is met or exceeded"""
        return self.current_quantity >= self.target_quantity

    @property
    def progress_percentage(self):
        if not self.target_quantity or self.target_quantity <= 0:
            return 0

        percentage = (self.current_quantity / self.target_quantity) * 100
        return min(round(percentage), 100)
    
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
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    title = models.CharField(max_length=255)
    message = models.TextField()
    is_read = models.BooleanField(default=False) # is_read TINYINT
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)