"""
URL configuration for IMS project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from inventory import views

urlpatterns = [
    path('', views.home, name='home'),
    path('login/', views.login_view, name='login'),
    path('admin/dashboard/', views.admin_dashboard, name='admin_dashboard'),

    path('inventory/dashboard/', views.inventory_dashboard, name='inventory_dashboard'),
    path('inventory/add/', views.add_product_view, name='add_product'),
    path('inventory/edit/<int:product_id>/', views.edit_product_view, name='edit_product'),
    path('inventory/delete/<int:product_id>/', views.delete_product_view, name='delete_product'),
    path('category/add/', views.add_category_view, name='add_category'),

    path('sales/dashboard/', views.sales_dashboard, name='sales_dashboard'),
    path('sales/history/', views.sales_history, name='sales_history'),
    path('sales/confirm/', views.process_sale, name='process_sale'),

    path('admin/dashboard/', views.admin_dashboard, name='admin_dashboard'),

    path('admin/manage/employees/', views.admin_manage_employee, name='admin_manage_employee'),
    path('admin/employee/add/', views.add_employee, name='add_employee'),
    path('admin/employee/edit/', views.edit_employee, name='edit_employee'),
    path('admin/employee/delete/', views.delete_employee, name='delete_employee'),
    path('inventory/admin/add/', views.admin_add_product_view, name='admin_add_product'),


    path('inventory/', views.admin_inventory_overview, name='admin_inventory_overview'),


    path('admin/', admin.site.urls),

]
