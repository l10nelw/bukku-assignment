import os
import sys
import django
from decimal import Decimal

# Set up Django BEFORE any Django imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

import django
django.setup()

from products.models import Product

print("=" * 80)
print("SEEDING PRODUCTS")
print("=" * 80)
print()

products = [
    {'name': 'ProductA', 'description': '', 'price': Decimal('2.00')},
]

created_count = 0
existing_count = 0
for product_data in products:
    try:
        # Check if product exists first
        product = Product.objects.filter(name=product_data['name']).first()
        if product:
            existing_count += 1
            print(f"⚠️  Product already exists: {product.name}")
        else:
            # Create new product
            product = Product.objects.create(**product_data)
            created_count += 1
            print(f"✅ Created product: {product.name}")
    except Exception as e:
        print(f"❌ Error processing {product_data['name']}: {str(e)}")

print()
print(f"Total products created: {created_count}")
print(f"Total products existing: {existing_count}")
print()
print("=" * 80)
