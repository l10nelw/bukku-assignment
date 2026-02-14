from rest_framework import serializers
from transactions.models import Transaction
from products.models import Product
from django.utils import timezone


class TransactionCreateSerializer(serializers.ModelSerializer):
    product_id = serializers.IntegerField(write_only=True)

    class Meta:
        model = Transaction
        fields = ['id', 'transaction_type', 'product_id', 'quantity', 'unit_price', 'transaction_datetime']
        read_only_fields = ['id']

    def validate_product_id(self, value):
        try:
            product = Product.objects.get(pk=value)
        except Product.DoesNotExist:
            raise serializers.ValidationError("Product not found.")
        return value

    def validate_quantity(self, value):
        if value <= 0:
            raise serializers.ValidationError("Quantity must be greater than 0.")
        return value

    def validate_unit_price(self, value):
        if value <= 0:
            raise serializers.ValidationError("Unit price must be greater than 0.")
        return value

    def validate_transaction_datetime(self, value):
        if value > timezone.now():
            raise serializers.ValidationError("Transaction datetime cannot be in the future.")
        return value

    def create(self, validated_data):
        product_id = validated_data.pop('product_id')
        product = Product.objects.get(pk=product_id)
        user = self.context['request'].user

        transaction = Transaction(
            user=user,
            product=product,
            **validated_data
        )
        transaction.save()
        return transaction


class TransactionUpdateSerializer(serializers.ModelSerializer):
    product_id = serializers.IntegerField(required=False)

    class Meta:
        model = Transaction
        fields = ['transaction_type', 'product_id', 'quantity', 'unit_price', 'transaction_datetime']

    def validate_product_id(self, value):
        try:
            Product.objects.get(pk=value)
        except Product.DoesNotExist:
            raise serializers.ValidationError("Product not found.")
        return value

    def validate_quantity(self, value):
        if value <= 0:
            raise serializers.ValidationError("Quantity must be greater than 0.")
        return value

    def validate_unit_price(self, value):
        if value <= 0:
            raise serializers.ValidationError("Unit price must be greater than 0.")
        return value

    def validate_transaction_datetime(self, value):
        if value > timezone.now():
            raise serializers.ValidationError("Transaction datetime cannot be in the future.")
        return value

    def update(self, instance, validated_data):
        # Update product if provided
        if 'product_id' in validated_data:
            product_id = validated_data.pop('product_id')
            instance.product = Product.objects.get(pk=product_id)

        # Update other fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        instance.save()
        return instance


class TransactionListSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source='product.name', read_only=True)
    cost = serializers.SerializerMethodField()

    class Meta:
        model = Transaction
        fields = [
            'id', 'transaction_type', 'product_name', 'quantity',
            'unit_price', 'total_price', 'transaction_datetime', 'cost', 'created_at'
        ]
        read_only_fields = fields

    def get_cost(self, obj):
        return obj.calculate_cost()
