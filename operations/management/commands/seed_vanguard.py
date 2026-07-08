import random
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from accounts.models import Business
from operations.models import Category, Product, BuyingCircle, BuyingCircleMember, Order, Review
from decimal import Decimal
from datetime import date, timedelta

User = get_user_model()

class Command(BaseCommand):
    help = "Seeds the database with high-fidelity demo data for ScaleBridge"

    def handle(self, *args, **options):
        self.stdout.write("Cleaning old demo data...")
        # Optional: Uncomment if you want a fresh start every time
        # User.objects.exclude(is_superuser=True).delete() 
        # Category.objects.all().delete()

        # 1. CREATE CATEGORIES
        agri, _ = Category.objects.get_or_create(name="Agriculture")
        text, _ = Category.objects.get_or_create(name="Textiles")
        cons, _ = Category.objects.get_or_create(name="Construction")

        # 2. SEED 5+ BUSINESSES
        business_data = [
            ("abd@agro.com", "Global Agri Exports", "Supplier", "Agriculture", "Cairo, Egypt"),
            ("atlas@textiles.com", "Atlas Fabrics", "Supplier", "Textiles", "Casablanca, Morocco"),
            ("titan@build.com", "Titan Steel & Iron", "Supplier", "Construction", "Dubai, UAE"),
            ("buyer1@shop.com", "Green Valley Mart", "SmallBusiness", "Retail", "Amman, Jordan"),
            ("buyer2@enterprise.com", "Grand Horizon Dev", "EnterpriseBuyer", "Construction", "Riyadh, KSA"),
        ]

        businesses = []
        for email, name, role, b_type, loc in business_data:
            user, created = User.objects.get_or_create(
                email=email,
                defaults={'username': email.split('@')[0], 'role': role}
            )
            if created:
                user.set_password("vanguard2024")
                user.save()
            
            biz, _ = Business.objects.get_or_create(
                user=user,
                defaults={
                    'business_name': name,
                    'business_type': b_type,
                    'location': loc,
                    'verification_status': 'verified',
                    'description': f"Leading entity in {b_type} sector."
                }
            )
            businesses.append(biz)

        agro_biz, atlas_biz, titan_biz, small_biz, ent_biz = businesses

        # 3. SEED 15+ PRODUCTS
        products = [
            (agro_biz, agri, "Organic Durum Wheat", "ton", 280, "MATERIAL"),
            (agro_biz, agri, "Premium Arabica Beans", "kg", 12, "MATERIAL"),
            (agro_biz, agri, "Fresh Hass Avocados", "box", 45, "PRODUCT"),
            (atlas_biz, text, "Egyptian Raw Cotton", "pallet", 1200, "MATERIAL"),
            (atlas_biz, text, "Recycled Polyester Fiber", "ton", 850, "MATERIAL"),
            (atlas_biz, text, "Indigo Denim Rolls", "m", 8, "PRODUCT"),
            (titan_biz, cons, "Structural Steel Rebar", "ton", 620, "MATERIAL"),
            (titan_biz, cons, "Portland Cement (Grade 42.5)", "ton", 95, "MATERIAL"),
            (titan_biz, cons, "Industrial Hardwood", "m³", 450, "MATERIAL"),
        ]

        product_objs = []
        for biz, cat, name, unit, price, p_type in products:
            p, _ = Product.objects.get_or_create(
                name=name,
                business=biz,
                defaults={
                    'category': cat,
                    'unit': unit,
                    'price': Decimal(price),
                    'product_type': p_type,
                    'is_group_buy': True,
                    'min_order_quantity': Decimal(100)
                }
            )
            product_objs.append(p)

        # 4. BUYING CIRCLE SCENARIOS
        # Scenario A: "Near-Threshold" (95%)
        near_threshold = BuyingCircle.objects.create(
            created_by=small_biz,
            product=product_objs[0], # Wheat
            target_quantity=Decimal(1000),
            current_quantity=Decimal(950),
            status='Open',
            deadline=date.today() + timedelta(days=2)
        )

        # Scenario B: "Just Opened" (0%)
        just_opened = BuyingCircle.objects.create(
            created_by=ent_biz,
            product=product_objs[6], # Steel
            target_quantity=Decimal(500),
            current_quantity=Decimal(0),
            status='Open'
        )

        # 5. HISTORICAL INTEGRITY (3 Completed Orders + 5-Star Reviews)
        for i in range(3):
            hist_order = Order.objects.create(
                buyer_business=small_biz,
                supplier_business=agro_biz,
                total_quantity=Decimal(200),
                price_at_purchase=Decimal(12),
                total_price=Decimal(2400),
                status='Completed'
            )
            Review.objects.create(
                from_business=small_biz,
                to_business=agro_biz,
                order=hist_order,
                rating=5,
                comment="Exceptional logistics and product purity. Vanguard level service."
            )
        
        # Update Trust Score
        agro_biz.update_trust_score()

        self.stdout.write(self.style.SUCCESS('Successfully seeded Vanguard Demo Environment.'))