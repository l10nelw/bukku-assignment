# Bukku Transaction Management System

A RESTful Django application for tracking purchase and sale transactions with JWT authentication and cost calculation using Weighted Average Cost (WAC) method.

## Features

- **JWT Authentication**: Secure user registration and login with JWT tokens
- **Transaction Management**: Full CRUD operations on purchase/sale transactions (Create, Read, Update, Delete)
- **Cost Calculation**: Automatic cost calculation using Weighted Average Cost (WAC) method
  - For purchases: Average cost per unit of all purchases up to transaction date
  - For sales: Cost of goods sold = WAC × Quantity Sold
- **On-the-fly Calculation**: Costs recalculated dynamically based on current inventory state
- **Retroactive Data Entry**: Supports out-of-order transaction creation with automatic cost recalculation
- **DateTime Support**: Precise timestamps with timezone awareness for transactions
- **Data Validation**:
  - No future-dated transactions allowed
  - Full CRUD operations enabled (PUT, PATCH, DELETE)
- **Product Management**: Pre-seeded dummy product (ProductA at RM2.00 base price)

## Project Structure

```
bukku-assignment/
├── config/               # Django project settings
│   ├── settings.py      # Configuration
│   ├── urls.py          # URL routing
│   └── wsgi.py
├── users/               # User authentication app
│   ├── models.py        # Custom User model
│   ├── views.py         # Auth views
│   ├── serializers.py   # User serializers
│   └── urls.py
├── products/            # Product management app
│   ├── models.py        # Product model
│   ├── migrations/      # Database migrations
│   └── serializers.py
├── transactions/        # Transaction management app
│   ├── models.py        # Transaction model with WAC cost calculation
│   ├── views.py         # Transaction viewsets (CRUD operations)
│   ├── serializers.py   # Transaction serializers
│   ├── migrations/      # Database migrations
│   └── urls.py
├── scripts/             # Utility scripts
│   ├── seed_products.py         # Seed ProductA to database
│   ├── clear_transactions.py    # Clear all transactions from DB
│   └── test_apis.py             # Comprehensive API endpoint testing
├── manage.py           # Django management script
├── requirements.txt    # Python dependencies
└── README.md          # This file
```

## Installation & Setup

### 1. Create Virtual Environment

```bash
python -m venv .venv
# On Windows:
.venv\Scripts\activate
# On macOS/Linux:
source .venv/bin/activate
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Apply Database Migrations

```bash
python manage.py migrate
```

### 4. Seed Products

```bash
python scripts/seed_products.py
```

This creates ProductA (base price: RM2.00)

### 5. Start Development Server

```bash
python manage.py runserver
```

Server will be available at `http://127.0.0.1:8000/`

## API Endpoints

### Authentication

#### Register User
```
POST /api/auth/register/
Content-Type: application/json

{
  "username": "john_doe",
  "email": "john@example.com",
  "password": "securepass123",
  "password_confirm": "securepass123",
  "first_name": "John",
  "last_name": "Doe"
}

Response: 201 Created
{
  "message": "User registered successfully",
  "user": {
    "id": 1,
    "username": "john_doe",
    "email": "john@example.com",
    "first_name": "John",
    "last_name": "Doe"
  }
}
```

#### Login
```
POST /api/auth/login/
Content-Type: application/json

{
  "username": "john_doe",
  "password": "securepass123"
}

Response: 200 OK
{
  "message": "Login successful",
  "user": {...},
  "tokens": {
    "refresh": "eyJhbGciOiJIUzI1NiIs...",
    "access": "eyJhbGciOiJIUzI1NiIs..."
  }
}
```

#### Get Profile
```
GET /api/auth/profile/
Authorization: Bearer <access_token>

Response: 200 OK
{
  "id": 1,
  "username": "john_doe",
  "email": "john@example.com",
  "first_name": "John",
  "last_name": "Doe"
}
```

### Transactions

All transaction endpoints require JWT authentication using the `Authorization: Bearer <access_token>` header.

#### Create Purchase Transaction
```
POST /api/transactions/
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "transaction_type": "purchase",
  "product_id": 1,
  "quantity": 150,
  "unit_price": "2.00",
  "transaction_datetime": "2022-01-01T10:00:00Z"
}

Response: 201 Created
{
  "message": "Transaction recorded successfully",
  "transaction": {
    "id": 1,
    "transaction_type": "purchase",
    "product_name": "ProductA",
    "quantity": 150,
    "unit_price": "2.00",
    "total_price": "300.00",
    "transaction_datetime": "2022-01-01T10:00:00Z",
    "cost": 2.0,
    "created_at": "2026-02-14T00:00:00Z"
  }
}
```

#### Create Sale Transaction
```
POST /api/transactions/
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "transaction_type": "sale",
  "product_id": 1,
  "quantity": 5,
  "unit_price": "2.50",
  "transaction_datetime": "2022-01-07T10:00:00Z"
}

Response: 201 Created
{
  "message": "Transaction recorded successfully",
  "transaction": {
    "id": 2,
    "transaction_type": "sale",
    "product_name": "ProductA",
    "quantity": 5,
    "unit_price": "2.50",
    "total_price": "12.50",
    "transaction_datetime": "2022-01-07T10:00:00Z",
    "cost": 9.84,
    "created_at": "2026-02-14T00:00:30Z"
  }
}
```

#### Get All Transactions
```
GET /api/transactions/
Authorization: Bearer <access_token>

Response: 200 OK
[
  {
    "id": 1,
    "transaction_type": "purchase",
    "product_name": "ProductA",
    "quantity": 150,
    "unit_price": "2.00",
    "total_price": "300.00",
    "transaction_datetime": "2022-01-01T10:00:00Z",
    "cost": 2.0,
    "created_at": "2026-02-14T00:00:00Z"
  },
  {
    "id": 2,
    "transaction_type": "sale",
    "product_name": "ProductA",
    "quantity": 5,
    "unit_price": "2.50",
    "total_price": "12.50",
    "transaction_datetime": "2022-01-07T10:00:00Z",
    "cost": 9.84,
    "created_at": "2026-02-14T00:00:30Z"
  }
]
```

#### Get Purchase Transactions Only
```
GET /api/transactions/purchases/
Authorization: Bearer <access_token>

Response: 200 OK
{
  "purchases": [...]
}
```

#### Get Sale Transactions Only
```
GET /api/transactions/sales/
Authorization: Bearer <access_token>

Response: 200 OK
{
  "sales": [...]
}
```

#### Update Transaction (PATCH)
```
PATCH /api/transactions/{id}/
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "quantity": 200
}

Response: 200 OK
{
  "message": "Transaction updated successfully",
  "transaction": {
    "id": 1,
    "quantity": 200,
    ...
  }
}
```

#### Replace Transaction (PUT)
```
PUT /api/transactions/{id}/
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "transaction_type": "purchase",
  "product_id": 1,
  "quantity": 200,
  "unit_price": "2.00",
  "transaction_datetime": "2022-01-01T10:00:00Z"
}

Response: 200 OK
{
  "message": "Transaction updated successfully",
  "transaction": {...}
}
```

#### Delete Transaction
```
DELETE /api/transactions/{id}/
Authorization: Bearer <access_token>

Response: 204 No Content
```

## Business Rules

### Transaction Features

1. **No Future Dates**: Transaction datetimes cannot be in the future
   ```
   Error Example:
   POST /api/transactions/  # with future datetime
   Response: 400 Bad Request
   {"error": "Transaction datetime cannot be in the future"}
   ```

2. **Retroactive Entry Support**: Transactions can be created out of chronological order
   - Add Purchase 1 (Jan 1)
   - Add Sale (Jan 7)
   - Add Purchase 2 (Jan 5) ← Retroactively, and Sale cost recalculates automatically

3. **Full CRUD Operations**:
   - Create: POST /api/transactions/
   - Read: GET /api/transactions/, GET /api/transactions/{id}/
   - Update: PATCH/PUT /api/transactions/{id}/
   - Delete: DELETE /api/transactions/{id}/

4. **User Isolation**: Each user has completely separate transactions and costs
   - User A's WAC for ProductA is independent of User B's
   - Transactions filtered by authenticated user only

### Cost Calculation (WAC Method)

For all transactions, cost is calculated using Weighted Average Cost (WAC):

**For Purchase Transactions:**
```
WAC = Total Purchase Cost / Total Units Purchased
```

**For Sale Transactions:**
```
Cost of Sale = WAC × Quantity Sold
```

**Example - Retroactive Entry Scenario:**
```
Step 1: Purchase 1 (Jan 1)
  150 units @ RM2.00 = RM300.00
  Cost: RM2.00 per unit (only purchase so far)

Step 2: Sale (Jan 7)
  Sell 5 units @ RM2.50 = RM12.50
  Cost: RM2.00 × 5 = RM10.00
  (Based only on Purchase 1)

Step 3: Add Purchase 2 retroactively (Jan 5)
  10 units @ RM1.50 = RM15.00
  Cost: (RM300 + RM15) / (150 + 10) = RM1.97 per unit

Step 4: Sale cost automatically RECALCULATED
  Cost: RM1.97 × 5 = RM9.84
  (Now includes both purchases)
```

**Key Feature**: On-the-fly calculation means retroactive entries automatically adjust all affected costs!

## Testing

### Automated API Testing

Run the comprehensive API test suite:
```bash
python scripts/test_apis.py
```

This tests:
- User registration and authentication
- Creating transactions
- Retroactive transaction creation with cost recalculation
- Reading transactions (all, purchases, sales)
- Updating transactions (PATCH)
- Deleting transactions
- Getting user profile

### Clear Transactions

Reset all transactions in the database:
```bash
python scripts/clear_transactions.py
```

Useful for clean testing between test runs.

### Manual Testing with cURL

#### Cross-Platform Note
All curl examples below use escaped quotes (`\"`) which work in **Windows CMD, PowerShell, Bash, and all Unix shells**.

#### Register User
```bash
curl -X POST http://localhost:8000/api/auth/register/ -H "Content-Type: application/json" -d "{\"username\": \"testuser\", \"email\": \"test@example.com\", \"password\": \"pass123\", \"password_confirm\": \"pass123\", \"first_name\": \"Test\", \"last_name\": \"User\"}"
```
```bash
curl -X POST http://localhost:8000/api/auth/register/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "email": "test@example.com",
    "password": "pass123",
    "password_confirm": "pass123",
    "first_name": "Test",
    "last_name": "User"
  }'
```

#### Login
```bash
curl -X POST http://localhost:8000/api/auth/login/ -H "Content-Type: application/json" -d "{\"username\": \"testuser\", \"password\": \"pass123\"}"
```

#### Get Profile
```bash
curl -H "Authorization: Bearer <access_token>" http://localhost:8000/api/auth/profile/
```

#### Create Purchase Transaction
```bash
curl -X POST http://localhost:8000/api/transactions/ -H "Authorization: Bearer <access_token>" -H "Content-Type: application/json" -d "{\"transaction_type\": \"purchase\", \"product_id\": 1, \"quantity\": 150, \"unit_price\": \"2.00\", \"transaction_datetime\": \"2022-01-01T10:00:00Z\"}"
```

#### Get All Transactions
```bash
curl -H "Authorization: Bearer <access_token>" http://localhost:8000/api/transactions/
```

#### Update Transaction (PATCH)
```bash
curl -X PATCH http://localhost:8000/api/transactions/1/ -H "Authorization: Bearer <access_token>" -H "Content-Type: application/json" -d "{\"quantity\": 200}"
```

#### Delete Transaction
```bash
curl -X DELETE http://localhost:8000/api/transactions/1/ -H "Authorization: Bearer <access_token>"
```

## Database Models

### User
```python
- id (Integer, Primary Key)
- username (String, Unique)
- email (String, Unique)
- password (Hashed)
- first_name (String)
- last_name (String)
- is_active (Boolean)
- is_staff (Boolean)
```

### Product
```python
- id (Integer, Primary Key)
- name (String, Unique)
- description (Text, Optional)
- price (Decimal)
- created_at (DateTime)
- updated_at (DateTime)
```

### Transaction
```python
- id (Integer, Primary Key)
- user (ForeignKey to User)
- product (ForeignKey to Product)
- transaction_type (Choice: 'purchase' or 'sale')
- quantity (Integer)
- unit_price (Decimal)
- total_price (Decimal, calculated)
- transaction_datetime (DateTime with timezone, indexed)
- created_at (DateTime, auto)

Indexes:
- user_id (for filtering by user)
- transaction_datetime (for ordering)
```

## Technologies Used

- **Framework**: Django 6.0.2
- **API**: Django REST Framework 3.14.0
- **Authentication**: djangorestframework-simplejwt 5.3.2
- **Database**: SQLite (development)
- **Python**: 3.12+
- **Currency**: Malaysian Ringgit (RM)

## Configuration

Key settings in `config/settings.py`:

```python
# JWT Configuration
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(hours=1),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=1),
    'ALGORITHM': 'HS256',
}

# REST Framework
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticated',
    ),
}

# Custom User Model
AUTH_USER_MODEL = 'users.User'

# Allow all hosts for development
ALLOWED_HOSTS = ['*']
```

## Error Handling

All endpoints return appropriate HTTP status codes:

- **201 Created**: Successful resource creation
- **200 OK**: Successful GET/PATCH/PUT request
- **204 No Content**: Successful DELETE request
- **400 Bad Request**: Validation error (e.g., future-dated transaction)
- **401 Unauthorized**: Missing or invalid authentication token
- **403 Forbidden**: Permission denied
- **404 Not Found**: Resource not found
- **500 Internal Server Error**: Server error

## Future Enhancements

- Batch transaction imports from CSV
- Transaction filtering by date range
- Profit/loss reports with charts
- Real-time inventory tracking
- Product categories and tags
- Transaction notes and attachments
- Admin dashboard with analytics
- Mobile app integration

## Documentation Files

- **README.md** (this file) - Complete system overview
- **QUICK_REFERENCE.md** - Quick API and script reference
- **PROJECT_SUMMARY.md** - High-level project information
- **SETUP.md** - Detailed setup instructions
- **API_TEST_RESULTS.md** - Latest API test results
- **INDEX.md** - Project index

## License

This project is open source and available under the MIT License.

## Support

For issues or questions, please refer to the documentation files or create an issue in the repository.
