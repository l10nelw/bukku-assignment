import os
import sys
import django

# Add parent directory to path to import Django modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from transactions.models import Transaction

print(f"Transactions before delete: {Transaction.objects.count()}")
Transaction.objects.all().delete()
print(f"Transactions after delete: {Transaction.objects.count()}")
