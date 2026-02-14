# Bukku Transaction Management System - File Index

## 📚 Documentation Files

**Start Here:**
1. [SETUP.md](SETUP.md) - Step-by-step setup and usage guide with examples
2. [README.md](README.md) - Complete API documentation with all endpoints
3. [PROJECT_SUMMARY.md](PROJECT_SUMMARY.md) - Project overview and technical details

**Reference:**
- [REQUIREMENTS_CHECKLIST.md](REQUIREMENTS_CHECKLIST.md) - Verification of all requirements
- [.env.example](.env.example) - Environment configuration template

## 🔧 Core Application Code

### Configuration (`config/`)
- `settings.py` - Django settings with JWT and DRF configuration
- `urls.py` - URL routing for all API endpoints
- `wsgi.py` - WSGI application configuration
- `asgi.py` - ASGI application configuration

### Users App (`users/`)
**Responsible for:** User authentication and management

Files:
- `models.py` - Custom User model (extends Django's AbstractUser)
- `views.py` - Authentication endpoints (register, login, profile)
- `serializers.py` - User data serializers
- `admin.py` - Django admin configuration
- `apps.py` - App configuration

Endpoints:
- `POST /api/auth/register/` - User registration
- `POST /api/auth/login/` - User login with JWT tokens
- `GET /api/auth/profile/` - Get authenticated user profile

### Products App (`products/`)
**Responsible for:** Product management and seeding

Files:
- `models.py` - Product model
- `serializers.py` - Product serializers
- `management/commands/seed_products.py` - Data seeding command
- `admin.py` - Django admin configuration
- `apps.py` - App configuration

Includes:
- 8 pre-defined dummy products
- Management command: `python manage.py seed_products`

### Transactions App (`transactions/`)
**Responsible for:** Purchase/sale transactions and cost calculation

Files:
- `models.py` - Transaction model with FIFO cost calculation
- `views.py` - Transaction ViewSet with filtering
- `serializers.py` - Transaction serializers with validation
- `admin.py` - Django admin configuration
- `apps.py` - App configuration

Endpoints:
- `POST /api/transactions/` - Create purchase or sale
- `GET /api/transactions/` - List all user transactions
- `GET /api/transactions/purchases/` - List purchases only
- `GET /api/transactions/sales/` - List sales with FIFO cost

## 🗄️ Database & Dependencies

- `db.sqlite3` - SQLite database (auto-created on migration)
- `requirements.txt` - Python package dependencies
- `migrations/` - Database migration files (in each app folder)

## 📝 Project Files

- `manage.py` - Django management utility
- `.gitignore` - Git ignore configuration
- `test_api_simple.py` - Automated API test script

## 🏗️ Application Architecture

```
bukku-assignment/
├── config/                    # Django Project
│   ├── settings.py           # Configuration (JWT, DRF, INSTALLED_APPS)
│   ├── urls.py               # Main URL router
│   ├── wsgi.py               # WSGI server
│   └── asgi.py               # ASGI server
│
├── users/                    # Authentication App
│   ├── models.py             # User model
│   ├── views.py              # Auth views
│   ├── serializers.py        # User serializers
│   ├── migrations/           # Database changes
│   └── ...
│
├── products/                 # Products App
│   ├── models.py             # Product model
│   ├── management/
│   │   └── commands/
│   │       └── seed_products.py  # Seeding command
│   ├── migrations/           # Database changes
│   └── ...
│
├── transactions/             # Transactions App
│   ├── models.py             # Transaction model (with FIFO)
│   ├── views.py              # Transaction views
│   ├── serializers.py        # Transaction serializers
│   ├── migrations/           # Database changes
│   └── ...
│
├── manage.py                 # Django CLI
├── db.sqlite3               # SQLite Database
├── requirements.txt         # Dependencies
├── .gitignore              # Git configuration
├── .env.example            # Environment template
│
└── Documentation/
    ├── README.md                    # Full API documentation
    ├── SETUP.md                     # Setup guide
    ├── PROJECT_SUMMARY.md           # Project overview
    ├── REQUIREMENTS_CHECKLIST.md    # Requirements verification
    └── INDEX.md                     # This file
```

## 🔐 Key Models & Fields

### User Model
```python
- id: Auto-generated primary key
- username: Unique username
- email: Unique email address
- password: Hashed password
- first_name, last_name: User name
- is_active, is_staff: Boolean flags
- date_joined: Automatic timestamp
```

### Product Model
```python
- id: Primary key
- name: Unique product name
- description: Optional description
- price: Decimal product price
- created_at, updated_at: Timestamps
```

### Transaction Model
```python
- id: Primary key
- user: ForeignKey to User
- transaction_type: Choice field (purchase/sale)
- product: ForeignKey to Product
- quantity: Integer quantity
- unit_price: Decimal unit price
- total_price: Decimal (calculated)
- transaction_date: Unique date per user
- created_at: Timestamp

Key Methods:
- clean(): Validates business rules
- save(): Calculates total_price
- calculate_cost(): FIFO cost calculation
```

## 🚀 Quick Start Sequence

1. **Read:** [SETUP.md](SETUP.md) for installation
2. **Install:** `pip install -r requirements.txt`
3. **Migrate:** `python manage.py migrate`
4. **Seed:** `python manage.py seed_products`
5. **Run:** `python manage.py runserver`
6. **Test:** Use endpoints from [README.md](README.md)

## 📖 API Quick Reference

### Authentication Endpoints
```
Register:  POST /api/auth/register/
Login:     POST /api/auth/login/
Profile:   GET  /api/auth/profile/  [Auth Required]
```

### Transaction Endpoints
```
Create:    POST /api/transactions/              [Auth Required]
List All:  GET  /api/transactions/              [Auth Required]
Purchases: GET  /api/transactions/purchases/    [Auth Required]
Sales:     GET  /api/transactions/sales/        [Auth Required]
```

## 💻 Development Notes

- **Framework:** Django 6.0.2
- **API:** Django REST Framework 3.14.0
- **Auth:** djangorestframework-simplejwt 5.3.2
- **Database:** SQLite3 (default)
- **Python:** 3.12+

## 🎯 Key Features Implemented

✅ JWT Authentication with token refresh
✅ User registration and login
✅ Purchase transaction recording
✅ Sale transaction recording
✅ FIFO cost calculation for sales
✅ Immutable transactions (no update/delete)
✅ Business rule validation (date, order, future)
✅ User-isolated transaction history
✅ RESTful API design
✅ Comprehensive error handling

## 📞 Support Files

- **Test Script:** `test_api_simple.py` - Run with `python test_api_simple.py`
- **Admin:** Create superuser with `python manage.py createsuperuser`
- **Admin URL:** `http://localhost:8000/admin/`

---

**All files are properly organized and ready for development, testing, and deployment.**

For detailed setup instructions, see [SETUP.md](SETUP.md)
For complete API documentation, see [README.md](README.md)
