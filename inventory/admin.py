from django.contrib import admin
from .models import Category, ProductInventory, Employee, Sale, SalesItem

class CategoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')

class ProductInventoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'sku_code', 'price', 'category', 'quantity', 'minimum_quantity', 'image_path', 'created_at', 'updated_at')

class EmployeeAdmin(admin.ModelAdmin):
    list_display = ('id', 'username', 'email', 'password', 'role', 'created_at')

class SaleAdmin(admin.ModelAdmin):
    list_display = ('id', 'total_amount', 'date')
    search_fields = ('id',)
    
    

class SalesItemAdmin(admin.ModelAdmin):
    list_display = ('sale', 'product', 'quantity', 'price')
    search_fields = ('sale__id', 'product__name')

    # Customizing 'price' to show the price from the related ProductInventory model
    def price(self, obj):
        return obj.product.price
    price.admin_order_field = 'product__price'
    price.short_description = 'Price'

admin.site.register(Category, CategoryAdmin)
admin.site.register(ProductInventory, ProductInventoryAdmin)
admin.site.register(Employee, EmployeeAdmin)
admin.site.register(Sale, SaleAdmin)
admin.site.register(SalesItem, SalesItemAdmin)
