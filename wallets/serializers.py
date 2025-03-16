from rest_framework_json_api import serializers
from rest_framework_json_api.relations import ResourceRelatedField
from .models import Wallet, Transaction


class WalletSerializer(serializers.ModelSerializer):

    class Meta:
        model = Wallet
        fields = ('id', 'label', 'balance')
        read_only_fields = ('balance',)
        schema_extra = {
            "example": {
                "data": {
                    "type": "wallets",
                    "attributes": {
                        "label": "My Wallet"
                    }
                }
            }
        }


class TransactionSerializer(serializers.ModelSerializer):
    wallet = ResourceRelatedField(queryset=Wallet.objects.all())

    class Meta:
        model = Transaction
        fields = ('id', 'txid', 'amount', 'wallet')
        schema_extra = {
            "example": {
                "data": {
                    "type": "transactions",
                    "attributes": {
                        "txid": "TX100",
                        "amount": "100.00"
                    },
                    "relationships": {
                        "wallet": {
                            "data": {
                                "type": "wallets",
                                "id": "1"
                            }
                        }
                    }
                }
            }
        }
