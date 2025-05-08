# 🗃️ Inventory Management System

The **Inventory Management System** is a web-based application built with **Django (Python)** for the backend and **HTML, CSS, JavaScript** for the frontend. It is designed to help retail businesses efficiently manage product stock, sales operations, and employee responsibilities through dedicated role-based dashboards.

---

## 🚀 Features

- 🔐 Role-based user authentication (Admin, Inventory Manager, Salesperson)
- 📦 Inventory and product management
- 🧾 Real-time sales with auto-updated stock levels
- 📈 Inventory status alerts (low stock, non-moving products)
- 🧠 Smart insights on top-selling and stagnant products
- 🧮 Sequential sale ID generation
- 🖥️ Clean, responsive dashboards tailored to each role

---

## 👥 User Roles

### 🔸 Admin
- Predefined user in the system
- Registers employees (Salesperson and Inventory Manager)
- Has access to all modules and dashboards

### 🔸 Inventory Manager
- Adds, updates, and deletes products and categories
- Manages stock quantities
- Views inventory reports and sales patterns
- Receives alerts for:
  - Frequently sold products
  - Products with no recent purchases
  - Low stock levels

### 🔸 Salesperson
- Views available inventory
- Searches for products and selects quantities to sell
- Validates quantities against available stock before proceeding
- On successful sale:
  - Inventory updates automatically
  - A unique sale ID is generated
- Access to:
  - Product inventory (read-only)
  - Today’s sales history
  - Invoices
- Buttons: **Proceed**, **Cancel Sale**, **Back**

---

## 🛠️ Tech Stack

- **Backend**: Django (Python)
- **Frontend**: HTML, CSS, JavaScript
- **Database**: SQLite (default), compatible with PostgreSQL/MySQL
- **Libraries**: Bootstrap, jQuery (optional)

---

## ⚙️ Installation & Setup

### 📋 Prerequisites
- Python 3.8+
- pip (Python package installer)
- Virtualenv (recommended for environment isolation)

### 🔧 Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/inventlix.com.git
cd inventlix.com

# Create and activate virtual environment
python -m venv venv
source venv/bin/activate       # On Windows: venv\Scripts\activate

# Install project dependencies
pip install -r requirements.txt

# Apply database migrations
python manage.py makemigrations
python manage.py migrate

# Create admin/superuser account
python manage.py createsuperuser

# Start the development server
python manage.py runserver
