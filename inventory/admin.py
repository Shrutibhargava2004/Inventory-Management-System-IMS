from django.contrib import admin
from .models import Category, ProductInventory, Employee

class CategoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')

class ProductInventoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'sku_code', 'price', 'category', 'quantity', 'minimum_quantity', 'image_path', 'created_at', 'updated_at')

class EmployeeAdmin(admin.ModelAdmin):
    list_display = ('id', 'username', 'email', 'password', 'role', 'created_at')

admin.site.register(Category, CategoryAdmin)
admin.site.register(ProductInventory, ProductInventoryAdmin)
admin.site.register(Employee, EmployeeAdmin)
