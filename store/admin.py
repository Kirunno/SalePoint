from django.contrib import admin
from .models import Category, Product, Cart, CartItem, Order, OrderItem


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')
    search_fields = ('name',)


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'price', 'old_price', 'is_available')
    list_filter = ('is_available', 'category')
    search_fields = ('name',)


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ('id', 'user')


@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    list_display = ('id', 'cart', 'product', 'quantity')


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'user', 'name', 'phone',
        'delivery_type', 'payment_type',
        'total_price', 'status', 'tracking_number',
        'created_at', 'updated_at'
    )
    list_filter = ('status', 'delivery_type', 'payment_type', 'created_at')
    search_fields = ('phone', 'name', 'tracking_number')

    def save_model(self, request, obj, form, change):
        if obj.status == "Отправлен" and not obj.tracking_number:
            from .views import generate_tracking_code
            obj.tracking_number = generate_tracking_code()
        super().save_model(request, obj, form, change)


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ('id', 'order', 'product', 'quantity', 'price')
