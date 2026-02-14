from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from transactions.models import Transaction
from transactions.serializers import TransactionCreateSerializer, TransactionListSerializer, TransactionUpdateSerializer


class TransactionViewSet(viewsets.ModelViewSet):
    """ViewSet for handling purchase and sale transactions"""
    permission_classes = [IsAuthenticated]
    http_method_names = ['get', 'post', 'put', 'patch', 'delete']

    def get_queryset(self):
        """Return transactions for the authenticated user"""
        return Transaction.objects.filter(user=self.request.user).order_by('transaction_datetime')

    def get_serializer_class(self):
        """Use different serializers for different actions"""
        if self.action == 'create':
            return TransactionCreateSerializer
        elif self.action in ['update', 'partial_update']:
            return TransactionUpdateSerializer
        return TransactionListSerializer

    def create(self, request, *args, **kwargs):
        """Create a new transaction (purchase or sale)"""
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            transaction = serializer.save()
            return Response(
                {
                    'message': 'Transaction recorded successfully',
                    'transaction': TransactionListSerializer(transaction).data
                },
                status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, *args, **kwargs):
        """Update a transaction"""
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=kwargs.get('partial', False))
        if serializer.is_valid():
            transaction = serializer.save()
            return Response(
                {
                    'message': 'Transaction updated successfully',
                    'transaction': TransactionListSerializer(transaction).data
                },
                status=status.HTTP_200_OK
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, *args, **kwargs):
        """Delete a transaction"""
        instance = self.get_object()
        instance.delete()
        return Response(
            {'message': 'Transaction deleted successfully'},
            status=status.HTTP_204_NO_CONTENT
        )

    def list(self, request, *args, **kwargs):
        """Retrieve all transactions for the user"""
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response(
            {
                'count': queryset.count(),
                'transactions': serializer.data
            },
            status=status.HTTP_200_OK
        )

    @action(detail=False, methods=['get'])
    def purchases(self, request):
        """Retrieve all purchase transactions"""
        queryset = self.get_queryset().filter(transaction_type='purchase')
        serializer = self.get_serializer(queryset, many=True)
        return Response(
            {
                'count': queryset.count(),
                'purchases': serializer.data
            },
            status=status.HTTP_200_OK
        )

    @action(detail=False, methods=['get'])
    def sales(self, request):
        """Retrieve all sale transactions with costing information"""
        queryset = self.get_queryset().filter(transaction_type='sale')
        serializer = self.get_serializer(queryset, many=True)
        return Response(
            {
                'count': queryset.count(),
                'sales': serializer.data
            },
            status=status.HTTP_200_OK
        )
