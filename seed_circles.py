"""
Run with:  python manage.py shell < seed_circles.py
Creates test users, businesses, categories, and a group-buy product
so you can walk through all buying circle scenarios in the browser.
"""

import os, django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ScaleBridge_B2B_Platform.settings')

from accounts.models import User, Business
from operations.models import Category, Product

# ── Categories ────────────────────────────────────────────────────────────────
cat, _ = Category.objects.get_or_create(name='Raw Materials')

# ── Enterprise supplier ───────────────────────────────────────────────────────
ent_user, _ = User.objects.get_or_create(
    email='enterprise@test.com',
    defaults=dict(username='enterprise', role='EnterpriseBuyer')
)
ent_user.set_password('Test1234!')
ent_user.save()

ent_biz, _ = Business.objects.get_or_create(
    user=ent_user,
    defaults=dict(
        business_name='AgroGiant Corp',
        business_type='Wholesale Supplier',
        location='Chicago, IL',
        description='Large-scale raw material supplier.',
        verification_status='verified',
    )
)

# ── Small Business 1 (circle starter) ────────────────────────────────────────
sb1_user, _ = User.objects.get_or_create(
    email='smallbiz1@test.com',
    defaults=dict(username='smallbiz1', role='SmallBusiness')
)
sb1_user.set_password('Test1234!')
sb1_user.save()

sb1_biz, _ = Business.objects.get_or_create(
    user=sb1_user,
    defaults=dict(
        business_name='Sunrise Bakery',
        business_type='Food Producer',
        location='Austin, TX',
        verification_status='verified',
    )
)

# ── Small Business 2 (circle joiner) ─────────────────────────────────────────
sb2_user, _ = User.objects.get_or_create(
    email='smallbiz2@test.com',
    defaults=dict(username='smallbiz2', role='SmallBusiness')
)
sb2_user.set_password('Test1234!')
sb2_user.save()

sb2_biz, _ = Business.objects.get_or_create(
    user=sb2_user,
    defaults=dict(
        business_name='Golden Mill Co.',
        business_type='Food Producer',
        location='Denver, CO',
        verification_status='verified',
    )
)

# ── Small Business 3 (the one that tips the circle over the target) ───────────
sb3_user, _ = User.objects.get_or_create(
    email='smallbiz3@test.com',
    defaults=dict(username='smallbiz3', role='SmallBusiness')
)
sb3_user.set_password('Test1234!')
sb3_user.save()

sb3_biz, _ = Business.objects.get_or_create(
    user=sb3_user,
    defaults=dict(
        business_name='Harvest Noodle Co.',
        business_type='Food Producer',
        location='Portland, OR',
        verification_status='verified',
    )
)

# ── Group-buy product (owned by enterprise supplier) ─────────────────────────
product, created = Product.objects.get_or_create(
    business=ent_biz,
    name='Industrial Grade Wheat Flour',
    defaults=dict(
        category=cat,
        description='High-gluten wheat flour suitable for industrial baking. Minimum bulk order applies.',
        unit='kg',
        price='0.85',
        currency='USD',
        product_type='MATERIAL',
        is_group_buy=True,
        min_order_quantity='1000',  # 1,000 kg minimum
    )
)

# ── Regular (non-group-buy) product to keep marketplace varied ────────────────
Product.objects.get_or_create(
    business=ent_biz,
    name='Refined Sunflower Oil',
    defaults=dict(
        category=cat,
        description='Cold-pressed sunflower oil in 20L drums.',
        unit='L',
        price='1.20',
        currency='USD',
        product_type='MATERIAL',
        is_group_buy=False,
    )
)

print()
print("=" * 58)
print("  Seed complete — test accounts ready")
print("=" * 58)
print()
print("  ENTERPRISE (supplier)")
print("    Email   : enterprise@test.com")
print("    Password: Test1234!")
print("    Business: AgroGiant Corp")
print()
print("  SMALL BUSINESS 1 (starts the circle)")
print("    Email   : smallbiz1@test.com")
print("    Password: Test1234!")
print("    Business: Sunrise Bakery")
print()
print("  SMALL BUSINESS 2 (joins the circle)")
print("    Email   : smallbiz2@test.com")
print("    Password: Test1234!")
print("    Business: Golden Mill Co.")
print()
print("  SMALL BUSINESS 3 (tips the circle over the target)")
print("    Email   : smallbiz3@test.com")
print("    Password: Test1234!")
print("    Business: Harvest Noodle Co.")
print()
print("  GROUP-BUY PRODUCT")
print(f"    Name    : {product.name}")
print(f"    Min Qty : {product.min_order_quantity} {product.unit}")
print(f"    Price   : {product.currency} {product.price} / {product.unit}")
print(f"    {'CREATED' if created else 'already existed'}")
print("=" * 58)
print()
