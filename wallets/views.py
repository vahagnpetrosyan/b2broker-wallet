from rest_framework import viewsets, permissions
from rest_framework_json_api import pagination
from .models import Wallet, Transaction
from .serializers import WalletSerializer, TransactionSerializer

class WalletViewSet(viewsets.ModelViewSet):
    """
    API endpoint for wallets, with list, create, retrieve, update, destroy.
    Supports filtering, sorting, and pagination as per JSON:API.
    """
    queryset = Wallet.objects.all().order_by('id')
    serializer_class = WalletSerializer
    permission_classes = [permissions.AllowAny]  # In the future we might restrict this.
    filterset_fields = ['label', 'balance']
    search_fields = ['label']
    ordering_fields = ['label', 'balance', 'id']
    ordering = ['id']


class TransactionViewSet(viewsets.ModelViewSet):
    """
    API endpoint for transactions, supporting JSON:API filtering/sorting.
    Creating a transaction will update the related wallet's balance.
    """
    queryset = Transaction.objects.select_related('wallet').all().order_by('id')
    serializer_class = TransactionSerializer
    permission_classes = [permissions.AllowAny] # In the future we might restrict this.
    filterset_fields = ['wallet', 'txid', 'amount']
    search_fields = ['txid']
    ordering_fields = ['txid', 'amount', 'id']
    ordering = ['id']
