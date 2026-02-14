from django.db import models
from django.core.exceptions import ValidationError
from django.utils import timezone
from decimal import Decimal
from users.models import User
from products.models import Product


class Transaction(models.Model):
    """Transaction model for purchase and sale records"""
    TRANSACTION_TYPE_CHOICES = [
        ('purchase', 'Purchase'),
        ('sale', 'Sale'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='transactions')
    transaction_type = models.CharField(max_length=10, choices=TRANSACTION_TYPE_CHOICES)
    product = models.ForeignKey(Product, on_delete=models.PROTECT, related_name='transactions')
    quantity = models.PositiveIntegerField()
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    total_price = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    transaction_datetime = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['transaction_datetime']
        indexes = [
            models.Index(fields=['user', 'transaction_datetime']),
            models.Index(fields=['transaction_type', 'transaction_datetime']),
        ]

    def clean(self):
        """Validate transaction constraints"""
        # Check date sequence (no transactions after now)
        if self.transaction_datetime > timezone.now():
            raise ValidationError("Transaction datetime cannot be in the future.")

    def save(self, *args, **kwargs):
        self.full_clean()
        # Calculate total price if not set
        if not self.total_price:
            self.total_price = self.quantity * self.unit_price
        super().save(*args, **kwargs)

    def calculate_cost(self):
        """
        Calculate average cost per unit at the moment of the transaction.
        For purchases: Average cost = Total cost of all purchases including this one / Total units including this one
        For sales: Cost of unit sold = Average cost per unit * Quantity sold
        """
        # Get all purchases of this product by the user before or on this transaction datetime
        purchases = Transaction.objects.filter(
            user=self.user,
            product=self.product,
            transaction_type='purchase',
            transaction_datetime__lte=self.transaction_datetime
        )

        # Calculate total cost and total units of all purchases up to this point
        total_purchase_cost = Decimal('0.00')
        total_units = 0
        for purchase in purchases:
            total_purchase_cost += purchase.total_price
            total_units += purchase.quantity

        if total_units == 0:
            return Decimal('0.00')

        average_cost_per_unit = total_purchase_cost / Decimal(total_units)

        if self.transaction_type == 'purchase':
            return round(average_cost_per_unit, 2)
        else:
            return round(average_cost_per_unit * self.quantity, 2)
