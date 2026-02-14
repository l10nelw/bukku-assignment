from django.contrib import admin
from transactions.models import Transaction

@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'transaction_type', 'product', 'quantity', 'unit_price', 'total_price', 'transaction_datetime')
    list_filter = ('transaction_type', 'transaction_datetime', 'created_at')
    search_fields = ('user__username', 'product__name')
    readonly_fields = ('total_price', 'created_at')
    ordering = ('-transaction_datetime',)
