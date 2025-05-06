from django.db import IntegrityError, transaction
from django.shortcuts import render, redirect
from django.contrib import messages
from .models import ProductInventory, Category, Employee, Sale, SalesItem
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import get_object_or_404
from django.http import HttpResponse ,JsonResponse
from django.db.models import F
from django.utils import timezone


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
        category_name = request.POST.get('name')  
        
        if category_name:
            existing_category = Category.objects.filter(name=category_name).first()
            
            if existing_category:
                messages.error(request, "Category with this name already exists.")
            else:
                try:
                    new_category = Category(name=category_name)
                    new_category.save()
                    messages.success(request, "Category added successfully.")
                except IntegrityError:
                    messages.error(request, "An error occurred while adding the category.")
        else:
            messages.error(request, "Category name cannot be empty.")

        return redirect('inventory_dashboard')  

    return redirect('inventory_dashboard') 

@login_required
def sales_dashboard(request):
    products = ProductInventory.objects.all()
    categories = Category.objects.all()
    return render(request, 'sales_dashboard.html', {
        'products': products,
        'categories': categories
    })

@login_required
def confirm_sale(request):
    if request.method == 'POST':
        # Get the list of selected products and quantities from the POST request
        sale_items = request.POST.getlist('sale_items')  # A list of product IDs and quantities
        total_amount = 0
        
        # Create the Sale record
        sale = Sale.objects.create(total_amount=total_amount)
        
        # Loop through the sale items and create SalesItem records
        for item in sale_items:
            product_id, quantity = item.split(':')  # Assuming format 'product_id:quantity'
            product = ProductInventory.objects.get(id=product_id)
            quantity = int(quantity)
            
            if product.quantity >= quantity:  # Check if enough stock is available
                # Create SalesItem record
                sales_item = SalesItem.objects.create(
                    sale=sale,
                    product=product,
                    quantity=quantity,
                    price=product.price,
                )
                
                # Update inventory
                product.quantity -= quantity
                product.save()

                # Add to total amount
                total_amount += product.price * quantity
            else:
                return JsonResponse({'error': 'Insufficient stock for product: ' + product.name})

        # Update the total amount in the sale record
        sale.total_amount = total_amount
        sale.save()

        # Return success message
        return JsonResponse({'success': 'Sale completed successfully', 'sale_id': sale.id})
    
    return JsonResponse({'error': 'Invalid request method'}, status=400)

@login_required
def sales_history(request):
    # Get the current date (ignoring time)
    today = timezone.now().date()

    # Fetch all sales for today
    sales = Sale.objects.filter(created_at__date=today)

    return render(request, 'sales_history.html', {'sales': sales})

def process_sale(request):
    if request.method == 'POST':
        # Assuming `selected_items` contains the selected product ids and quantities from the form
        selected_items = request.POST.getlist('selected_items')  # A list of product_id:quantity pairs
        total_amount = 0
        sale_items = []
        
        # Start a transaction to ensure that both Sale and SalesItems are created correctly
        with transaction.atomic():
            # Create a new Sale entry
            sale = Sale(total_amount=0)  # Total amount is set later after calculating the sale items
            sale.save()

            for item in selected_items:
                product_id, quantity = item.split(':')
                product = ProductInventory.objects.get(id=product_id)
                quantity = int(quantity)
                
                if product.quantity < quantity:
                    messages.error(request, f"Not enough stock for {product.name}")
                    return redirect('sales_dashboard')  # Redirect to the sales dashboard if not enough stock
                
                # Create the SalesItem entry
                sales_item = SalesItem(
                    sale=sale,
                    product=product,
                    quantity=quantity,
                    price=product.price
                )
                sales_item.save()
                sale_items.append(sales_item)
                
                # Update the product quantity in inventory
                product.quantity -= quantity
                product.save()
                
                # Calculate total amount for the sale
                total_amount += product.price * quantity

            # Update the Sale's total amount after all items are added
            sale.total_amount = total_amount
            sale.save()

            # Success message
            messages.success(request, f"Sale completed successfully! Total: ₹{total_amount}")
            
        # Redirect to a page after processing the sale (e.g., sales dashboard or sales history)
        return redirect('sales_dashboard')

    return render(request, 'sales_dashboard.html')