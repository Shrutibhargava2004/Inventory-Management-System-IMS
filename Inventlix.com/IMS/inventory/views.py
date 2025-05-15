from django.db import IntegrityError
from django.shortcuts import render, redirect
from django.contrib import messages
from .models import ProductInventory, Category, Employee, Sale, SalesItem
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import get_object_or_404
from django.http import JsonResponse
from django.db.models import F, Sum, Q
from django.utils import timezone


# Create your views here.

def home(request):
    return render(request, 'index.html')

def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        role = request.POST['role']
        next_url = request.POST.get('next', '')  # get from POST

        try:
            user = Employee.objects.get(username=username, role=role)
            if user.password == password:
                request.session['username'] = user.username
                request.session['role'] = user.role
                if next_url:
                    return redirect(next_url)
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
    username = request.session.get('username')
    if not username:
        return redirect('login')
    try:
        employee = Employee.objects.get(username=username)
    except Employee.DoesNotExist:
        messages.error(request, "Employee not found.")
        return redirect('login')
    products = ProductInventory.objects.all()
    categories = Category.objects.all()
    return render(request, 'sales_dashboard.html', {
        'products': products,
        'categories': categories,
        'employee': employee
    })


@login_required
def sales_history(request):
    today = timezone.now().date()  # Get today's date in the user's timezone
    print(f"Today's date: {today}")  # Debugging line to check today's date

    # Try to fetch the sales for today
    sales = Sale.objects.filter(date__date=today)
    print(f"Sales found: {sales.count()}")  # Debugging line to check how many sales are found

    return render(request, 'sales_history.html', {'sales': sales})

@login_required
def process_sale(request):
    if request.method == 'POST':
        try:
            employee = Employee.objects.get(username=request.session.get('username'))
        except Employee.DoesNotExist:
            return JsonResponse({'error': 'Salesperson not found in the Employee database'})

        sale_items_str = request.POST.get('sale_items', '')
        if not sale_items_str:
            return JsonResponse({'error': 'No valid products selected'})

        sale_items_list = sale_items_str.split(',')  # ["3:2", "5:1"]
        total_amount = 0

        sale = Sale.objects.create(salesperson=employee, total_amount=0)  # initial total

        for item in sale_items_list:
            try:
                product_id, quantity = item.split(':')
                product = ProductInventory.objects.get(id=int(product_id))
                quantity = int(quantity)
            except (ValueError, ProductInventory.DoesNotExist):
                continue  # skip invalid entries

            if product.quantity >= quantity:
                sales_item = SalesItem.objects.create(
                    sale=sale,
                    product=product,
                    quantity=quantity,
                    price_per_unit=product.price
                )
                product.quantity -= quantity
                product.save()

                total_amount += product.price * quantity
            else:
                return JsonResponse({'error': f'Insufficient stock for product: {product.name}'})

        sale.total_amount = total_amount
        sale.save()

        return JsonResponse({'success': 'Sale completed successfully', 'sale_id': sale.id})

    return JsonResponse({'error': 'Invalid request method'}, status=400)

@login_required
def admin_dashboard(request):
    total_employees = Employee.objects.count()
    total_products = ProductInventory.objects.count()
    today = timezone.now().date()
    todays_sales = Sale.objects.filter(date__date=today).aggregate(total_sales=Sum('total_amount'))['total_sales'] or 0

    products = ProductInventory.objects.all()

    low_stock_items = products.filter(quantity__lt=F('minimum_quantity')) 
    low_stock_count = low_stock_items.count()

    
    context = {
        'total_employees': total_employees,
        'total_products': total_products,
        'todays_sales': todays_sales,
        'low_stock_count': low_stock_count,
        'products': products,
        'low_stock_items': low_stock_items,
    }

    return render(request, 'admin_dashboard.html', context)

def admin_manage_employee(request):
    employees = Employee.objects.all()
    return render(request, 'admin_manage_employee.html', {'employees': employees})

def edit_employee(request):
    if request.method == "POST":
        emp = get_object_or_404(Employee, id=request.POST['id'])
        emp.username = request.POST['name']
        emp.email = request.POST['email']
        emp.role = request.POST['role']
        emp.save()
        messages.success(request, "Employee updated successfully.")
    return redirect('admin_manage_employee') 

def delete_employee(request):
    if request.method == "POST":
        emp = get_object_or_404(Employee, id=request.POST['id'])
        emp.delete()
        messages.success(request, "Employee deleted successfully.")
    return redirect('admin_manage_employee')

def add_employee(request):
    if request.method == 'POST':
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']
        role = request.POST['role']

        if Employee.objects.filter(username=username).exists():
            messages.error(request, "Username already exists.")
            return redirect('admin_manage_employee') 

        employee = Employee(username=username, email=email, role=role)
        employee.set_password(password) 
        employee.save()

        messages.success(request, "Employee added successfully.")
        return redirect('admin_manage_employee')  
    return redirect('admin_manage_employee')  

def admin_inventory_overview(request):
    search_query = request.GET.get('q', '')
    category_id = request.GET.get('category', '')
    stock_status = request.GET.get('stock', '')
    products = ProductInventory.objects.all()
    if search_query:
        products = products.filter(name__icontains=search_query)
    if category_id:
        products = products.filter(category_id=category_id)
        
    if stock_status == 'in':
        products = products.filter(quantity__gt=0)  # In stock: quantity > 0
    elif stock_status == 'low':
        products = products.filter(quantity__lte=F('minimum_quantity'), quantity__gt=0)
    elif stock_status == 'out':
        products = products.filter(quantity=0)

    low_stock_products = ProductInventory.objects.filter(quantity__lt=F('minimum_quantity'))
    categories = Category.objects.all()

    context = {
        'products': products,
        'low_stock_products': low_stock_products,
        'categories': categories
    }
    return render(request, 'admin_inventory_overview.html', context)

def admin_add_product_view(request):
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
        return redirect('admin_inventory_overview')

    categories = Category.objects.all()
    return render(request, 'add_product.html', {'categories': categories})

def delete_product_view(request, product_id):
    product = get_object_or_404(ProductInventory, id=product_id)
    product.delete()
    messages.success(request, "Product deleted successfully.")
    return redirect('admin_inventory_overview')
