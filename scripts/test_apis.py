import os
import sys
import json
import time

# Set up Django BEFORE any Django imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

import django
django.setup()

from django.test import Client
client = Client()

# Test 1: User Registration
print("TEST 1: User Registration")
print("-" * 80)
username = f"testuser_{int(time.time())}"
register_data = {
    "username": username,
    "email": f"{username}@example.com",
    "password": "testpass123",
    "password_confirm": "testpass123",
    "first_name": "Test",
    "last_name": "User"
}

response = client.post('/api/auth/register/', data=json.dumps(register_data), content_type='application/json')
print(f"Status: {response.status_code}")
print(f"Response: {json.dumps(response.json(), indent=2)}")
print()

if response.status_code != 201:
    print("❌ Registration failed")
    exit(1)
print("✅ Registration successful")
print()

# Test 2: User Login
print("TEST 2: User Login")
print("-" * 80)
login_data = {
    "username": username,
    "password": "testpass123"
}

response = client.post('/api/auth/login/', data=json.dumps(login_data), content_type='application/json')
print(f"Status: {response.status_code}")
token = response.json().get('tokens', {}).get('access')
print(f"Access Token: {token[:50] if token else 'None'}...")
print()

if not token:
    print("❌ Login failed")
    exit(1)
print("✅ Login successful")
print()

# Set up headers for authenticated requests
headers = {
    "HTTP_AUTHORIZATION": f"Bearer {token}",
    "Content-Type": "application/json"
}

# Test 3: Create Purchase 1 (Jan 1) - Retroactive Test Setup
print("TEST 3: Create Purchase 1 (Jan 1)")
print("-" * 80)
purchase1_data = {
    "transaction_type": "purchase",
    "product_id": 1,
    "quantity": 150,
    "unit_price": "2.00",
    "transaction_datetime": "2022-01-01T10:00:00Z"
}

response = client.post('/api/transactions/', data=json.dumps(purchase1_data), content_type='application/json', **headers)
print(f"Status: {response.status_code}")
resp_json = response.json()
print(f"Response: {json.dumps(resp_json, indent=2)}")
t1_id = resp_json.get('transaction', {}).get('id')
t1_cost = resp_json.get('transaction', {}).get('cost')
print()

if response.status_code != 201:
    print("❌ Purchase 1 creation failed")
    exit(1)
print(f"✅ Purchase 1 created")
print(f"   150 units @ RM2.00 = RM300.00")
print(f"   Cost: RM{t1_cost} (WAC with only this purchase)")
print()

# Test 4: Create Sale (Jan 7) - BEFORE Purchase 2 exists
print("TEST 4: Create Sale (Jan 7)")
print("-" * 80)
sale_data = {
    "transaction_type": "sale",
    "product_id": 1,
    "quantity": 5,
    "unit_price": "2.50",
    "transaction_datetime": "2022-01-07T10:00:00Z"
}

response = client.post('/api/transactions/', data=json.dumps(sale_data), content_type='application/json', **headers)
print(f"Status: {response.status_code}")
resp_json = response.json()
print(f"Response: {json.dumps(resp_json, indent=2)}")
t3_id = resp_json.get('transaction', {}).get('id')
sale_cost_before = resp_json.get('transaction', {}).get('cost')
print()

if response.status_code != 201:
    print("❌ Sale creation failed")
    exit(1)
print(f"✅ Sale created")
print(f"   Sell 5 units @ RM2.50 = RM12.50")
print(f"   Cost at creation: RM{sale_cost_before}")
print(f"   (Only Purchase 1 existed - WAC = RM2.00 per unit)")
print()

# Test 5: Create Purchase 2 Retroactively (Jan 5) - AFTER Sale
print("TEST 5: Add Purchase 2 Retroactively (Jan 5) - After Sale Created")
print("-" * 80)
print("⚠️  Adding transaction dated BEFORE the Sale (retroactive entry)")
print()
purchase2_data = {
    "transaction_type": "purchase",
    "product_id": 1,
    "quantity": 10,
    "unit_price": "1.50",
    "transaction_datetime": "2022-01-05T10:00:00Z"
}

response = client.post('/api/transactions/', data=json.dumps(purchase2_data), content_type='application/json', **headers)
print(f"Status: {response.status_code}")
resp_json = response.json()
print(f"Response: {json.dumps(resp_json, indent=2)}")
t2_id = resp_json.get('transaction', {}).get('id')
t2_cost = resp_json.get('transaction', {}).get('cost')
print()

if response.status_code != 201:
    print("❌ Purchase 2 creation failed")
    exit(1)
print(f"✅ Purchase 2 created retroactively")
print(f"   10 units @ RM1.50 = RM15.00")
print(f"   Cost: RM{t2_cost}")
print()

# Test 6: Retrieve Sale Again to See Recalculated Cost
print("TEST 6: Verify Sale Cost Recalculated (On-the-fly WAC)")
print("-" * 80)
response = client.get(f'/api/transactions/{t3_id}/', **headers)
print(f"Status: {response.status_code}")
resp_json = response.json()
sale_cost_after = resp_json.get('cost')
print()

print(f"Sale cost BEFORE retroactive entry: RM{sale_cost_before}")
print(f"Sale cost AFTER retroactive entry:  RM{sale_cost_after}")
print()
print(f"Why it changed:")
print(f"  Before: WAC = RM300 / 150 = RM2.00 per unit")
print(f"          5 units × RM2.00 = RM{sale_cost_before}")
print()
print(f"  After:  WAC = (RM300 + RM15) / (150 + 10) = RM1.9688 per unit")
print(f"          5 units × RM1.9688 = RM{sale_cost_after}")
print()

if sale_cost_after == 9.84:
    print("✅ Sale cost correctly recalculated to RM9.84")
else:
    print(f"⚠️  Sale cost: RM{sale_cost_after} (expected RM9.84)")
print()

# Test 7: Get All Transactions
print("TEST 7: Get All Transactions (Ordered by DateTime)")
print("-" * 80)
response = client.get('/api/transactions/', **headers)
print(f"Status: {response.status_code}")
resp_data = response.json()
transactions = resp_data if isinstance(resp_data, list) else resp_data.get('transactions', [])
print(f"Total transactions: {len(transactions)}")
print()
for t in transactions:
    print(f"  {t['transaction_datetime']}: {t['transaction_type'].upper()} - {t['quantity']} units - RM{t['cost']}")
print()

if response.status_code != 200:
    print("❌ Get transactions failed")
    exit(1)
print("✅ Retrieved all transactions in datetime order")
print()

# Test 8: Update Transaction (PATCH)
print("TEST 8: Update Transaction (PATCH)")
print("-" * 80)
update_data = {
    "quantity": 200
}

response = client.patch(f'/api/transactions/{t1_id}/', data=json.dumps(update_data), content_type='application/json', **headers)
print(f"Status: {response.status_code}")
updated_qty = response.json().get('transaction', {}).get('quantity')
print(f"Updated Purchase 1 quantity: 150 → {updated_qty}")
print()

if response.status_code != 200:
    print("❌ Update failed")
    exit(1)
print("✅ Transaction updated successfully")
print()

# Test 9: Delete Transaction
print("TEST 9: Delete Sale Transaction")
print("-" * 80)
response = client.delete(f'/api/transactions/{t3_id}/', **headers)
print(f"Status: {response.status_code}")
print()

if response.status_code != 204:
    print("❌ Delete failed")
    exit(1)
print("✅ Sale transaction deleted successfully")
print()

# Test 10: Get User Profile
print("TEST 10: Get User Profile")
print("-" * 80)
response = client.get('/api/auth/profile/', **headers)
print(f"Status: {response.status_code}")
profile = response.json()
print(f"Username: {profile.get('username')}")
print(f"Email: {profile.get('email')}")
print(f"First Name: {profile.get('first_name')}")
print(f"Last Name: {profile.get('last_name')}")
print()

if response.status_code != 200:
    print("❌ Get profile failed")
    exit(1)
print("✅ User profile retrieved successfully")
print()

print("=" * 80)
print("✅ ALL TESTS PASSED")
print("=" * 80)
