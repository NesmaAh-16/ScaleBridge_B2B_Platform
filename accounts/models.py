from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    # Mapping ENUM('Admin', 'SmallBusiness', 'EnterpriseBuyer') from Image 3
    ROLE_CHOICES = [
        ('Admin', 'Admin'),
        ('SmallBusiness', 'Small Business'),
        ('EnterpriseBuyer', 'Enterprise Buyer'),
    ]
    
    email = models.EmailField(unique=True) # email_UNIQUE from ERD
    phone = models.CharField(max_length=100, blank=True, null=True)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='SmallBusiness')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Use email as the primary login identifier instead of username
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'role']

    def __str__(self):
        return self.email

class Business(models.Model):
    # user_id INT (ForeignKey to users)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='businesses')
    business_name = models.CharField(max_length=255)
    business_type = models.CharField(max_length=100)
    location = models.CharField(max_length=45)
    description = models.TextField(blank=True, null=True)
    verification_status = models.CharField(max_length=45, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    logo = models.ImageField(upload_to='business_logos/', null=True, blank=True)

    def __str__(self):
        return self.business_name
    
    average_rating = models.DecimalField(max_digits=3, decimal_places=2, default=0.00),
    review_count = models.PositiveIntegerField(default=0),

    # Replace the old @property with this more robust version
    def update_trust_score(self):
        """Calculates and saves the new average rating and count."""
        reviews = self.reviews_received.all()
        self.review_count = reviews.count()
        if self.review_count > 0:
            total = sum([r.rating for r in reviews])
            self.average_rating = total / self.review_count
        else:
            self.average_rating = 0.00
        self.save()