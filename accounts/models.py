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

    def __str__(self):
        return self.business_name