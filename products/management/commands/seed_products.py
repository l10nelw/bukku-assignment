from django.core.management.base import BaseCommand
from products.models import Product
from decimal import Decimal


class Command(BaseCommand):
    help = 'Seed the database with dummy products'

    def handle(self, *args, **options):
        products = [
            {'name': 'ProductA', 'description': '', 'price': Decimal('2.00')},
        ]

        created_count = 0
        for product_data in products:
            product, created = Product.objects.get_or_create(**product_data)
            if created:
                created_count += 1
                self.stdout.write(
                    self.style.SUCCESS(f'Created product: {product.name}'))
            else:
                self.stdout.write(
                    self.style.WARNING(f'Product already exists: {product.name}'))

        self.stdout.write(
            self.style.SUCCESS(f'\nTotal products created: {created_count}'))
