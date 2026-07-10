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

        # 1. CREATE CATEGORIES
        agri, _ = Category.objects.get_or_create(name="Agriculture")
        text, _ = Category.objects.get_or_create(name="Textiles")
        cons, _ = Category.objects.get_or_create(name="Construction")

        # 2. CREATE THE ADMIN USER
        # admiMns@example.com, pass: nesma1234
        admin_user, created = User.objects.get_or_create(
            email="admiMns@example.com",
            defaults={
                'username': 'admin_nesma', 
                'role': 'Admin',
                'is_staff': True,
                'is_superuser': True
            }
        )
        admin_user.set_password("nesma1234")
        admin_user.save()
        self.stdout.write("Admin user created.")

        # 3. SEED BUSINESSES (Integrated your specific users)
        # Format: (email, password, business_name, role, business_type, location)
        business_data = [
            ("abd@agro.com", "vanguard2024", "Global Agri Exports", "Supplier", "Agriculture", "Cairo, Egypt"),
            ("atlas@textiles.com", "vanguard2024", "Atlas Fabrics", "Supplier", "Textiles", "Casablanca, Morocco"),
            ("titan@build.com", "vanguard2024", "Titan Steel & Iron", "Supplier", "Construction", "Dubai, UAE"),
            ("nesmalubbad@gmail.com", "nosa1234", "Nesma Small Business", "SmallBusiness", "Retail", "Gaza, Palestine"),
            ("mahmoudsameer059@gmail.com", "mah12345", "Mahmoud Enterprise", "EnterpriseBuyer", "Construction", "Gaza, Palestine"),
            ("shaimaamahmoudobaid@gmail.com", "sha12345", "Shaimaa Textile Group", "EnterpriseBuyer", "Textiles", "Gaza, Palestine"),
        ]

        businesses = []
        for email, password, name, role, b_type, loc in business_data:
            user, created = User.objects.get_or_create(
                email=email,
                defaults={'username': email.split('@')[0], 'role': role}
            )
            # We update password every time to ensure it matches your request
            user.set_password(password)
            user.save()
            
            biz, _ = Business.objects.update_or_create(
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

        # Unpack the first 5 for the rest of the script logic
        agro_biz, atlas_biz, titan_biz, small_biz, ent_biz = businesses[:5]

        # 4. SEED PRODUCTS
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

        # 5. BUYING CIRCLE SCENARIOS
        near_threshold = BuyingCircle.objects.create(
            created_by=small_biz,
            product=product_objs[0], 
            target_quantity=Decimal(1000),
            current_quantity=Decimal(950),
            status='Open',
            deadline=date.today() + timedelta(days=2)
        )

        just_opened = BuyingCircle.objects.create(
            created_by=ent_biz,
            product=product_objs[6], 
            target_quantity=Decimal(500),
            current_quantity=Decimal(0),
            status='Open'
        )

        # 6. HISTORICAL INTEGRITY
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
        
        agro_biz.update_trust_score()

        self.stdout.write(self.style.SUCCESS('Successfully seeded Vanguard Demo Environment with requested users.'))