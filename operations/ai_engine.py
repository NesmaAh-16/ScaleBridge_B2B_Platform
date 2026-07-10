from .models import Product, BuyingCircle
from django.db.models import Q

class DiscoveryEngine:
    @staticmethod
    def get_personalized_recommendations(business):
        """
        Refined Logic:
        1. Vertical Matching: Manufacturers need Materials; Artisans need Products.
        2. Exclusion: Never recommend a business's own products.
        3. Fail-safe: If no targeted match is found, show trending products.
        """
        if not business:
            return {'products': Product.objects.none(), 'circles': []}

        # 1. Determine what this business likely needs based on their category
        # These keys must match your <option value="..."> in business_profile.html
        category_map = {
            'LocalManufacturer': 'MATERIAL',
            'Supplier': 'MATERIAL',
            'Artisan': 'PRODUCT',
            'Farmer': 'MATERIAL',
        }
        
        target_type = category_map.get(business.business_type, 'PRODUCT')

        # 2. Targeted Query
        suggested_products = Product.objects.filter(
            product_type=target_type
        ).exclude(business=business).order_by('?')[:4]

        # 3. Fail-safe: If suggested_products is empty, just get the newest products
        # This ensures the "Generating..." message disappears
        if not suggested_products.exists():
            suggested_products = Product.objects.exclude(
                business=business
            ).order_by('-created_at')[:4]

        # 4. Urgency Logic for Circles
        trending_circles = BuyingCircle.objects.filter(
            status='Open'
        ).exclude(created_by=business).order_by('-current_quantity')[:2]

        return {
            'products': suggested_products,
            'circles': trending_circles
        }