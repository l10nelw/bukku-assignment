# Bukku Transaction System - Setup Guide

## Quick Start

### Prerequisites
- Python 3.12 or higher
- pip (Python package installer)
- Git (optional, for cloning)

### Step-by-Step Setup

#### 1. Clone or Download the Project
```bash
cd bukku-assignment
```

#### 2. Create a Virtual Environment
```bash
# Windows
python -m venv .venv
.venv\Scripts\activate

# macOS/Linux
python3 -m venv .venv
source .venv/bin/activate
```

#### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

#### 4. Initialize Database
```bash
python manage.py migrate
```

#### 5. Seed Sample Product (optional for testing)
```bash
python manage.py seed_products
```

This creates a sample product for testing. You can view it in the admin panel or make an API call.

#### 6. Start the Development Server
```bash
python manage.py runserver
```

The API will be available at: `http://127.0.0.1:8000/`

## Using the API

### 1. Register a User

**Request:**
```bash
curl -X POST http://127.0.0.1:8000/api/auth/register/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "john",
    "email": "john@example.com",
    "password": "secure123",
    "password_confirm": "secure123",
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
    "email": "john@example.com",
    "first_name": "John",
    "last_name": "Doe"
  }
}
```

### 2. Login to Get Tokens

**Request:**
```bash
curl -X POST http://127.0.0.1:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "john",
    "password": "secure123"
  }'
```

**Response:**
```json
{
  "message": "Login successful",
  "user": {...},
  "tokens": {
    "refresh": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "access": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
  }
}
```

**⚠️ Important**: Save the `access` token - you'll need it for all subsequent requests!

### 3. Get Your Profile (Optional)

**Request:**
```bash
curl -X GET http://127.0.0.1:8000/api/auth/profile/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

### 4. Record a Purchase Transaction

**Request:**
```bash
curl -X POST http://127.0.0.1:8000/api/transactions/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "transaction_type": "purchase",
    "product_id": 1,
    "quantity": 10,
    "unit_price": "800.00",
    "transaction_date": "2026-02-01"
  }'
```

**Response:**
```json
{
  "message": "Transaction recorded successfully",
  "transaction": {
    "id": 1,
    "transaction_type": "purchase",
    "product_name": "Laptop",
    "quantity": 10,
    "unit_price": "800.00",
    "total_price": "8000.00",
    "transaction_date": "2026-02-01",
    "cost": null,
    "created_at": "2026-02-09T18:50:00Z"
  }
}
```

### 5. Record a Sale Transaction

**Request:**
```bash
curl -X POST http://127.0.0.1:8000/api/transactions/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "transaction_type": "sale",
    "product_id": 1,
    "quantity": 5,
    "unit_price": "1200.00",
    "transaction_date": "2026-02-03"
  }'
```

**Note**: The `cost` field shows the cost of goods sold (FIFO method):
- If you purchased 10 laptops @ $800 each, the cost of selling 5 = 5 * $800 = $4000
- Sale revenue = 5 * $1200 = $6000
- Profit = $6000 - $4000 = $2000

### 6. View All Transactions

**Request:**
```bash
curl -X GET http://127.0.0.1:8000/api/transactions/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

### 7. View Only Purchase Transactions

**Request:**
```bash
curl -X GET http://127.0.0.1:8000/api/transactions/purchases/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

### 8. View Only Sale Transactions (with Cost Calculation)

**Request:**
```bash
curl -X GET http://127.0.0.1:8000/api/transactions/sales/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

## Understanding the Business Rules

### Rule 1: One Transaction Per Date
You cannot have more than one transaction on the same date.

**❌ This will fail:**
```bash
# First transaction on 2026-02-05
POST /api/transactions/ with date: "2026-02-05"  ✓ Success

# Second transaction on same date - FAILS
POST /api/transactions/ with date: "2026-02-05"  ✗ Error: "Only one transaction per date is allowed."
```

**✓ This works:**
```bash
POST /api/transactions/ with date: "2026-02-05"  ✓ Success
POST /api/transactions/ with date: "2026-02-06"  ✓ Success
```

### Rule 2: Chronological Order
Transactions must be in order (oldest first, newest last).

**❌ This will fail:**
```bash
# Create transaction for Feb 10
POST /api/transactions/ with date: "2026-02-10"  ✓ Success

# Try to create transaction for Feb 05 (earlier)
POST /api/transactions/ with date: "2026-02-05"  ✗ Error: "Transactions must be created in chronological order"
```

**✓ This works:**
```bash
POST /api/transactions/ with date: "2026-02-05"  ✓ Success
POST /api/transactions/ with date: "2026-02-10"  ✓ Success
```

### Rule 3: No Future Dates
Transaction dates cannot be in the future.

**❌ This will fail:**
```bash
POST /api/transactions/ with date: "2026-02-15" (future date)  ✗ Error: "Transaction date cannot be in the future."
```

### Rule 4: Immutable Transactions
Once a transaction is recorded, it cannot be modified or deleted.

**❌ This doesn't work:**
```bash
PUT /api/transactions/1/   ✗ Method not allowed
DELETE /api/transactions/1/ ✗ Method not allowed
PATCH /api/transactions/1/  ✗ Method not allowed
```

## FIFO Cost Calculation Example

Let's say you have these transactions:

```
Date: 2026-02-01
Purchase: 10 Laptops @ $800 each = $8000

Date: 2026-02-03
Purchase: 5 Laptops @ $900 each = $4500

Date: 2026-02-05
Sale: 8 Laptops @ $1200 each = $9600
```

**Cost Calculation (FIFO)**:
1. First 8 laptops come from the oldest purchase
2. Take 8 from the first purchase (10 available @ $800)
3. Cost = 8 * $800 = $6400
4. Profit = Revenue - Cost = $9600 - $6400 = $3200

**Response includes:**
- `total_price`: $9600 (what you sold for)
- `cost`: $6400 (what it cost you)
- Profit margin: ($9600 - $6400) / $9600 = 33.3%

## Troubleshooting

### "Connection refused" error
**Problem**: Can't connect to the API
**Solution**: Make sure the server is running with `python manage.py runserver`

### "401 Unauthorized" error
**Problem**: Missing or invalid access token
**Solution**:
1. Make sure you logged in and got the access token
2. Include it in the Authorization header: `Authorization: Bearer <token>`

### "400 Bad Request" error
**Problem**: Validation error with transaction
**Solution**: Check:
1. All required fields are present
2. Product ID exists (get from products list)
3. Transaction date is in the correct format (YYYY-MM-DD)
4. You're not creating duplicate dates or out-of-order dates

### "500 Internal Server Error"
**Problem**: Server error
**Solution**:
1. Check the server logs (in the terminal running the server)
2. Ensure database migrations are applied: `python manage.py migrate`
3. Try restarting the server

## Next Steps

- Review the [README.md](README.md) for complete API documentation
- Explore the Django admin panel at `http://127.0.0.1:8000/admin/` (create a superuser first)
- Modify product prices or add new products
- Implement additional features like reports or analytics

## Creating a Superuser (Admin)

To access the Django admin panel:

```bash
python manage.py createsuperuser
```

Then visit: `http://127.0.0.1:8000/admin/`

Use the Django admin to:
- View all users and transactions
- Manage products
- View application statistics

## Support

If you encounter issues:
1. Check the error message carefully
2. Review the README.md for API documentation
3. Check the server logs for detailed error information
4. Verify your request format matches the examples above
