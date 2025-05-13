from django.contrib import admin
from django.db import models  # Added for F() in restock_products
from .models.product import Product
from .models.order import Order
from .models.category import Category
from .models.customer import Customer

# Register Product model
@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'price', 'category', 'brand', 'quantity')
    search_fields = ('name', 'brand')
    list_filter = ('category',)
    list_editable = ('price', 'quantity')
    ordering = ('name',)
    actions = ['restock_products']

    def restock_products(self, request, queryset):
        """Increase stock quantity by 10 for selected products."""
        updated = queryset.update(quantity=models.F('quantity') + 10)
        self.message_user(request, f"{updated} product(s) restocked with 10 additional units.")
    restock_products.short_description = "Restock selected products (+10 units)"

# Register Category model
@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)
    ordering = ('name',)

# Register Order model
@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('product', 'customer', 'date_ordered', 'price', 'status')
    list_filter = ('status', 'date_ordered', 'customer')
    search_fields = ('product__name', 'customer__first_name', 'customer__last_name', 'customer__phone')
    list_editable = ('status',)
    actions = ['mark_as_shipped', 'mark_as_delivered', 'mark_as_cancelled']
    ordering = ('-date_ordered',)

    def mark_as_shipped(self, request, queryset):
        queryset.update(status='Shipped')
        self.message_user(request, "Selected orders marked as Shipped.")
    mark_as_shipped.short_description = "Mark selected orders as Shipped"

    def mark_as_delivered(self, request, queryset):
        queryset.update(status='Delivered')
        self.message_user(request, "Selected orders marked as Delivered.")
    mark_as_delivered.short_description = "Mark selected orders as Delivered"

    def mark_as_cancelled(self, request, queryset):
        queryset.update(status='Cancelled')
        self.message_user(request, "Selected orders marked as Cancelled.")
    mark_as_cancelled.short_description = "Mark selected orders as Cancelled"

# Register Customer model
@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ('first_name', 'last_name', 'phone', 'id')
    search_fields = ('first_name', 'last_name', 'phone')
    list_filter = ('last_name',)
    ordering = ('last_name', 'first_name')