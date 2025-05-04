from django.db import IntegrityError
from django.shortcuts import render, redirect
from django.contrib import messages
from .models import ProductInventory, Category, Employee
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import get_object_or_404
from django.http import HttpResponse
from django.db.models import F


# Create your views here.

def home(request):
    return render(request, 'index.html')

def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        role = request.POST['role']

        try:
            user = Employee.objects.get(username=username, role=role)
            if user.password == password: 
                # Save user session
                request.session['username'] = user.username
                request.session['role'] = user.role

                # Redirect to role-specific dashboard
                if role == 'admin':
                    return redirect('admin_dashboard')
                elif role == 'inventory_manager':
                    return redirect('inventory_dashboard')
                elif role == 'salesperson':
                    return redirect('sales_dashboard')
            else:
                messages.error(request, "Incorrect password.")
        except Employee.DoesNotExist:
            messages.error(request, "Invalid username or role.")
    
    return render(request, 'login.html')

def sales_dashboard(request):
    return HttpResponse("Welcome to Salesperson Dashboard!")

def admin_dashboard(request):
    return HttpResponse("Welcome to Admin Dashboard!")

@login_required
def inventory_dashboard(request):
    username = request.session.get('username')
    if not username:
        return redirect('login')
    try:
        employee = Employee.objects.get(username=username)
    except Employee.DoesNotExist:
        messages.error(request, "Employee not found.")
        return redirect('login')
    search_query = request.GET.get('q', '')
    category_id = request.GET.get('category', '')
    products = ProductInventory.objects.all()

    if search_query:
        products = products.filter(name__icontains=search_query)

    if category_id:
        products = products.filter(category_id=category_id)

    low_stock_products = products.filter(quantity__lt=F('minimum_quantity'))

    context = {
        'products': products,
        'low_stock_products': low_stock_products,
        'categories': Category.objects.all(),
        'employee': employee,  # Pass the full employee object
    }
    return render(request, 'inventory_dashboard.html', context)

@csrf_exempt 
def add_product_view(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        sku_code = request.POST.get('sku_code')
        price = request.POST.get('price')
        category_id = request.POST.get('category')
        quantity = request.POST.get('quantity')
        minimum_quantity = request.POST.get('minimum_quantity')

        image_path = request.POST.get('image_path')  # Just saving path string

        if ProductInventory.objects.filter(sku_code=sku_code).exists():
            messages.error(request, "SKU code already exists.")
            return redirect('add_product')

        category = Category.objects.get(id=category_id)
        product = ProductInventory.objects.create(
            name=name,
            sku_code=sku_code,
            price=price,
            category=category,
            quantity=quantity,
            minimum_quantity=minimum_quantity,
            image_path=image_path
        )
        messages.success(request, "Product added successfully.")
        return redirect('inventory_dashboard')

    categories = Category.objects.all()
    return render(request, 'add_product.html', {'categories': categories})

def edit_product_view(request, product_id):
    product = get_object_or_404(ProductInventory, id=product_id)

    if request.method == 'POST':
        product.name = request.POST.get('name')
        product.sku_code = request.POST.get('sku_code')
        product.price = request.POST.get('price')
        product.quantity = request.POST.get('quantity')
        product.minimum_quantity = request.POST.get('minimum_quantity')
        product.image_path = request.POST.get('image_path')
        category_id = request.POST.get('category')

        product.category = Category.objects.get(id=category_id)
        product.save()

        messages.success(request, "Product updated successfully.")
        return redirect('inventory_dashboard')

    categories = Category.objects.all()
    context = {
        'product': product,
        'categories': categories
    }
    return render(request, 'edit_product.html', context)

def delete_product_view(request, product_id):
    product = get_object_or_404(ProductInventory, id=product_id)
    product.delete()
    messages.success(request, "Product deleted successfully.")
    return redirect('inventory_dashboard')

@login_required
def add_category_view(request):
    if request.method == 'POST':
        category_name = request.POST.get('name')  # Retrieve the name from the form
        
        if category_name:
            # Check if the category already exists
            existing_category = Category.objects.filter(name=category_name).first()
            
            if existing_category:
                messages.error(request, "Category with this name already exists.")
            else:
                try:
                    # Create a new category
                    new_category = Category(name=category_name)
                    new_category.save()
                    messages.success(request, "Category added successfully.")
                except IntegrityError:
                    messages.error(request, "An error occurred while adding the category.")
        else:
            messages.error(request, "Category name cannot be empty.")

        return redirect('inventory_dashboard')  # Redirect to the dashboard after attempting to add category

    return redirect('inventory_dashboard')  # If not a POST request, redirect to the dashboard



