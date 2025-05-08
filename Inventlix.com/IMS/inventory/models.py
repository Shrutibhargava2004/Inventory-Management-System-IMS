from django.db import models
from django.contrib import admin

# Create your models here.

# Category Model
class Category(models.Model):
    name = models.CharField(max_length=100)
    def __str__(self):
        return self.name

# ProductInventory Model
class ProductInventory(models.Model):
    name = models.CharField(max_length=255)
    sku_code = models.CharField(max_length=100, unique=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    minimum_quantity = models.IntegerField(default=10)
    quantity = models.IntegerField()
    image_path = models.ImageField(upload_to='product_images/', blank=True, null=True)  # Using ImageField instead of CharField
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    def __str__(self):
        return self.name

# Employee Model
class Employee(models.Model):
    ROLE_CHOICES = [
        ('admin', 'Admin'),
        ('inventory_manager', 'Inventory Manager'),
        ('salesperson', 'Salesperson'),
    ]
    username = models.CharField(max_length=100, unique=True)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=255)
    role = models.CharField(choices=ROLE_CHOICES, max_length=20)
    created_at = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return self.username

class Sale(models.Model):
    salesperson = models.ForeignKey(Employee, on_delete=models.CASCADE)
    date = models.DateTimeField(auto_now_add=True)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    def __str__(self):
        return f"Sale #{self.id} by {self.salesperson.username}"

class SalesItem(models.Model):
    sale = models.ForeignKey(Sale, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey(ProductInventory, on_delete=models.CASCADE)
    quantity = models.IntegerField()
    price_per_unit = models.DecimalField(max_digits=10, decimal_places=2)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.product.name} (x{self.quantity})"
    
    def save(self, *args, **kwargs):
        # Automatically calculate the total price for this item
        self.total_price = self.quantity * self.price_per_unit
        super().save(*args, **kwargs)
