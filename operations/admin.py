from django.contrib import admin
from .models import Category, Product, BuyingCircle, BuyingCircleMember, Order, Review, Notification

# 1. Register Categories (This is what you are looking for!)
@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'created_at')
    search_fields = ('name',)

# 2. Register Products
@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'business', 'product_type', 'price', 'is_group_buy')
    list_filter = ('product_type', 'is_group_buy', 'category')
    search_fields = ('name', 'business__business_name')

# 3. Register Buying Circles
@admin.register(BuyingCircle)
class BuyingCircleAdmin(admin.ModelAdmin):
    list_display = ('product', 'target_quantity', 'current_quantity', 'status')
    list_filter = ('status',)

# 4. Register Orders
@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'buyer_business', 'supplier_business', 'total_price', 'status')
    list_filter = ('status',)

# 5. Register other models simply
admin.site.register(BuyingCircleMember)
admin.site.register(Review)
admin.site.register(Notification)