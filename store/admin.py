from django.contrib import admin
from .models import Category, Product, CartItem, Cart, Order, OrderItem

# Register your models here.
@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('name', )}
    list_display = ['name']


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'price', 'available']
    list_filter = ['available', 'category']
    prepopulated_fields = {'slug': ('name', )}

admin.site.register(Cart)    
admin.site.register(CartItem)


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    readonly_fields = ('product', 'price', 'quantity')
    extra = 0


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'full_name', 'created_at', 'status', 'total']
    inlines = [OrderItemInline]
    readonly_fields = ('created_at',)