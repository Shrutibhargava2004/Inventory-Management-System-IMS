# 🗃️ Inventory Management System

The **Inventory Management System** is a web-based application built using **Django (Python)** for the backend and **HTML, CSS, JavaScript** for the frontend. It is designed for retail businesses to manage inventory and sales operations effectively, using role-based dashboards for Inventory Managers and Salespersons.

---

## 🚀 Features

- 🔐 Role-based user login
- 📦 Product and inventory management
- 🧾 Sale recording with automatic stock updates
- 📈 Reports and insights on stock and sales
- 🧮 Sequential sale ID generation
- 🖥️ Clean and responsive dashboards

---

## 👥 User Roles

### 🔸 Inventory Manager

- Adds, updates, and deletes products and categories
- Manages product stock levels
- Views inventory trends and product performance
- Receives alerts for:
  - Frequently sold products
  - Products that haven’t been purchased recently
  - Low stock levels

### 🔸 Salesperson

- Views and searches available products
- Selects products and inputs sale quantity
- Validates input quantity against available stock
- Proceeds to confirm sales and generate sale records
- Product stock automatically updates after a sale
- Can view:
  - Inventory list (read-only)
  - Today’s sales history
  - Generated invoices
- Interface includes: **Proceed**, **Cancel Sale**, **Back** buttons

---

## 🛠️ Tech Stack

- **Backend**: Django (Python)
- **Frontend**: HTML, CSS, JavaScript
- **Database**: SQLite (default)
- **Other Libraries**: Bootstrap

---

## ⚙️ Installation & Setup

### 📋 Prerequisites

- Python 3.8+
- pip
- Virtualenv (recommended)

### 🔧 Setup Instructions

```bash
# Clone the repository
git clone https://github.com/Shrutibhargava2004/Inventory-Management-System-Inventlix
cd inventlix.com

# Create and activate virtual environment
python -m venv venv
venv\Scripts\activate #(On Windows)

# Install dependencies
pip install -r requirements.txt

# Apply database migrations
python manage.py makemigrations
python manage.py migrate

# Create users from the system manually
python manage.py runserver
```
🧪 Usage Workflow
- Inventory Manager logs in and manages inventory data.
- Salesperson logs in and performs sales using the available inventory.
- Sales are validated and recorded with auto-updated stock levels.
- Each user has access to features relevant to their role only.

📌 Future Enhancements
- PDF generation of invoices and reports
- Visual dashboard with charts
- API integration
- Stock alert notifications via email
- Barcode scanning support

