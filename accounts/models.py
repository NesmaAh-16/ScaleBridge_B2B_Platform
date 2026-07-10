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
    
    average_rating = models.DecimalField(max_digits=3, decimal_places=2, default=0.00)
    review_count = models.PositiveIntegerField(default=0)

    def update_trust_score(self):
        """
        AI Logic: Calculates a 1-5 star score by blending 
        Manual Stars with Automated Fulfillment KPIs.
        """
        # We import inside to avoid circular import errors
        from operations.models import Order
        from django.db.models import Avg

        # 1. Qualitative: Average of manual reviews
        reviews = self.reviews_received.all()
        avg_review = reviews.aggregate(Avg('rating'))['rating__avg'] or 0

        # 2. Quantitative: Fulfillment KPIs (The "Data-Driven" Requirement)
        orders = Order.objects.filter(supplier_business=self)
        total_orders = orders.count()
        
        if total_orders > 0:
            completed = orders.filter(status='Completed').count()
            cancelled = orders.filter(status='CANCELLED').count()
            # Penalty for cancellations: Successful / (Successful + Penalized Failures)
            # We multiply by 5 to get it on the 1-5 star scale
            kpi_score = (completed / (completed + (cancelled * 1.5))) * 5
        else:
            kpi_score = 5.0 # New businesses start with high trust

        # 3. Final Algorithm: 60% weight on reviews, 40% on fulfillment performance
        calculated_score = (float(avg_review) * 0.6) + (float(kpi_score) * 0.4)
        print("\n" + "="*40)
        print(f"-> Manual Star Avg: {avg_review}/5")
        print(f"-> Fulfillment KPI: {round(kpi_score, 2)}/5 (Success vs. Cancellations)")
        print(f"-> FINAL WEIGHTED SCORE: {round(calculated_score, 2)}")
        print("="*40 + "\n")
        print(f"🤖 AI REPUTATION AUDIT: {self.business_name}")
        # Save results to the database
        self.average_rating = round(min(calculated_score, 5.0), 2)
        self.review_count = total_orders
        self.save()