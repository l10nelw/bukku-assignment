# Bukku API Quick Reference Card

## Installation (One-Time Setup)

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Create database
python manage.py migrate

# 3. Add sample products
python scripts/seed_products.py

# 4. Start server
python manage.py runserver
```

## Authentication Flow

### 1. Register User
```bash
curl -X POST http://localhost:8000/api/auth/register/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "john",
    "email": "john@example.com",
    "password": "pass123",
    "password_confirm": "pass123",
    "first_name": "John",
    "last_name": "Doe"
  }'
```

**Response:**
```json
{
  "message": "User registered successfully",
  "user": {
    "id": 1,
    "username": "john",
    "email": "john@example.com"
  }
}
```

### 2. Login & Get Token
```bash
curl -X POST http://localhost:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"username": "john", "password": "pass123"}'
```

**Response:**
```json
{
  "tokens": {
    "access": "eyJhbGciOi...",  # Use this for requests
    "refresh": "eyJhbGciOi..."
  }
}
```

### 3. Use Token for API Calls
```bash
curl -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  http://localhost:8000/api/transactions/
```

## Transaction Operations

### Create Purchase
```bash
curl -X POST http://localhost:8000/api/transactions/ \
  -H "Authorization: Bearer TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "transaction_type": "purchase",
    "product_id": 1,
    "quantity": 10,
    "unit_price": "850.00",
    "transaction_datetime": "2026-02-01T10:00:00Z"
  }'
```

**Response includes `cost` field** (calculated at retrieval time):
```json
{
  "id": 1,
  "transaction_type": "purchase",
  "product_name": "ProductA",
  "quantity": 10,
  "unit_price": "850.00",
  "total_price": "8500.00",
  "cost": "850.00",
  "transaction_datetime": "2026-02-01T10:00:00Z",
  "created_at": "2026-02-13T10:00:00Z"
}
```

### Create Sale
```bash
curl -X POST http://localhost:8000/api/transactions/ \
  -H "Authorization: Bearer TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "transaction_type": "sale",
    "product_id": 1,
    "quantity": 5,
    "unit_price": "1200.00",
    "transaction_datetime": "2026-02-05T10:00:00Z"
  }'
```

**Response:**
```json
{
  "id": 2,
  "transaction_type": "sale",
  "product_name": "ProductA",
  "quantity": 5,
  "unit_price": "1200.00",
  "total_price": "6000.00",
  "cost": "4250.00",
  "transaction_datetime": "2026-02-05T10:00:00Z",
  "created_at": "2026-02-13T10:00:00Z"
}
```

### Get All Transactions
```bash
curl -H "Authorization: Bearer TOKEN" \
  http://localhost:8000/api/transactions/
```

### Update Transaction (PUT - full update)
```bash
curl -X PUT http://localhost:8000/api/transactions/1/ \
  -H "Authorization: Bearer TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "transaction_type": "purchase",
    "product_id": 1,
    "quantity": 15,
    "unit_price": "850.00",
    "transaction_datetime": "2026-02-01T10:00:00Z"
  }'
```

### Partial Update Transaction (PATCH)
```bash
curl -X PATCH http://localhost:8000/api/transactions/1/ \
  -H "Authorization: Bearer TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"quantity": 20}'
```

### Delete Transaction
```bash
curl -X DELETE http://localhost:8000/api/transactions/1/ \
  -H "Authorization: Bearer TOKEN"
```

## Cost Calculation Details

### Weighted Average Cost (WAC) Method

**Formula:**
```
WAC = (Total Cost of All Purchases) / (Total Units Purchased)
Cost for Sale = WAC × Quantity Sold
```

**Example:**
- Jan 1: Purchase 150 units @ RM2.00 = RM300.00
- Jan 5: Purchase 10 units @ RM1.50 = RM15.00
- Jan 7: Sell 5 units
  - WAC = (RM300 + RM15) / (150 + 10) = RM1.9688
  - Sale Cost = RM1.9688 × 5 = RM9.84 (rounded to RM9.84)

### Key Behavior

- **Costs are calculated on-the-fly**: Retrieved fresh every time you fetch a transaction
- **Retroactive entries work**: If you add a purchase dated Jan 5 after creating a sale on Jan 7, the sale cost automatically recalculates
- **Rounded to 2 decimals**: All cost values are rounded to 2 decimal places

## Utility Scripts

### Seed Products
```bash
python scripts/seed_products.py
```
Seed the database with ProductA (base price: RM2.00). Can be run multiple times safely.

### Clear All Transactions
```bash
python scripts/clear_transactions.py
```
Remove all transactions from the database (useful for clean testing).

### Test Retroactive Transaction Creation
```bash
python scripts/test_retroactive.py
```
Test adding transactions out of order and verify WAC costs are recalculated correctly.

### Test API Endpoints
```bash
python scripts/test_apis.py
```
Comprehensive API test suite covering registration, authentication, CRUD operations, and WAC calculations.

bash
curl -H "Authorization: Bearer TOKEN" \
  http://localhost:8000/api/transactions/
```

### Get Purchases Only
```bash
curl -H "Authorization: Bearer TOKEN" \
  http://localhost:8000/api/transactions/purchases/
```

### Get Sales with Cost
```bash
curl -H "Authorization: Bearer TOKEN" \
  http://localhost:8000/api/transactions/sales/
```

## Important Details

### Product IDs (From seed_products)
```
1 = ProductA (RM2.00)
```

### Date Format
Use `YYYY-MM-DD` format:
```
"transaction_date": "2026-02-15"
```

### Price Format
Use decimal with 2 places:
```
"unit_price": "850.00"
```

## WAC Cost Calculation

When you retrieve transactions, the `cost` field shows:

```
Cost = Weighted Average Cost per Unit × Quantity
WAC = (Total Cost of All Purchases) / (Total Units Purchased)
```

**Example:**
```
Purchase 1: 150 units @ RM2.00 (Jan 1)
Purchase 2: 10 units @ RM1.50 (Jan 5)
Sale: 5 units @ RM2.50 (Jan 7)

WAC = (RM300 + RM15) / (150 + 10) = RM1.97 per unit
Cost = 5 × RM1.97 = RM9.84
Revenue = 5 × RM2.50 = RM12.50
Profit = RM12.50 - RM9.84 = RM2.66
```

## Business Rules

### ❌ Will Fail:
```
# Duplicate date (same user, same date)
Date 2026-02-05: Purchase created ✓
Date 2026-02-05: Sale creation ✗ (FAIL: only one per date)

# Out of order
Date 2026-02-10: Sale created ✓
Date 2026-02-05: Purchase creation ✗ (FAIL: must be oldest first)

# Future date
Date 2026-12-25 (today is Feb 9, 2026)
Transaction creation ✗ (FAIL: no future dates)
```

### ✅ Will Succeed:
```
# Different dates (same user)
Date 2026-02-05: Purchase created ✓
Date 2026-02-06: Sale created ✓

# Chronological order
Date 2026-02-01: Purchase created ✓
Date 2026-02-05: Sale created ✓
Date 2026-02-10: Purchase created ✓

# Current or past dates
Date 2026-02-09 (today)
Date 2026-02-08 (yesterday)
Both OK ✓
```

## Error Examples

### Missing Token
```
Status: 401 Unauthorized
"Authentication credentials were not provided."
```

### Duplicate Date
```
Status: 400 Bad Request
"Only one transaction per date is allowed."
```

### Invalid Product
```
Status: 400 Bad Request
"Product not found."
```

### Future Date
```
Status: 400 Bad Request
"Transaction date cannot be in the future."
```

## Useful Django Commands

```bash
# Check project setup
python manage.py check

# List all migrations
python manage.py showmigrations

# Create new superuser for admin
python manage.py createsuperuser

# Access Django shell
python manage.py shell

# Run custom command
python manage.py seed_products

# Create migrations (after model changes)
python manage.py makemigrations

# Apply migrations
python manage.py migrate

# Run development server
python manage.py runserver
python manage.py runserver 0.0.0.0:8000  # Accessible externally
```

## Admin Panel

**URL:** http://localhost:8000/admin/

**Create superuser first:**
```bash
python manage.py createsuperuser
```

**Features:**
- View all users, products, transactions
- Create/edit/delete products
- View transaction history
- User management

## Response Structure

### Success Response
```json
{
  "message": "Operation successful",
  "data": { ... }
}
```

### Error Response
```json
{
  "error": "Error description",
  "details": { ... }
}
```

## HTTP Status Codes

| Code | Meaning | Example |
|------|---------|---------|
| 200 | OK | GET successful |
| 201 | Created | POST successful |
| 400 | Bad Request | Validation error |
| 401 | Unauthorized | Missing/invalid token |
| 403 | Forbidden | Permission denied |
| 404 | Not Found | Resource doesn't exist |
| 500 | Server Error | Unexpected error |

## Testing

### Run Test Script
```bash
python test_api_simple.py
```

### Manual Testing
See [SETUP.md](SETUP.md) for detailed examples

## Files to Review

| File | Purpose |
|------|---------|
| [README.md](README.md) | Complete API documentation |
| [SETUP.md](SETUP.md) | Installation & setup guide |
| [PROJECT_SUMMARY.md](PROJECT_SUMMARY.md) | Technical overview |
| [transactions/models.py](transactions/models.py) | FIFO logic implementation |
| [transactions/views.py](transactions/views.py) | Transaction endpoints |

## Key Endpoints Summary

```
POST   /api/auth/register/           Register new user
POST   /api/auth/login/              Get JWT tokens
GET    /api/auth/profile/            Get current user

POST   /api/transactions/            Create transaction
GET    /api/transactions/            List all transactions
GET    /api/transactions/purchases/  List purchases
GET    /api/transactions/sales/      List sales with cost
```

## Token Management

### Access Token
- **Lifetime:** 1 hour
- **Use:** Add to Authorization header
- **Format:** `Authorization: Bearer <access_token>`

### Refresh Token
- **Lifetime:** 1 day
- **Use:** Get new access token when expired
- **Endpoint:** `POST /api/auth/token/refresh/` (if implemented)

---

**Quick Tip:** Always include `-H "Content-Type: application/json"` when using cURL with POST requests!
