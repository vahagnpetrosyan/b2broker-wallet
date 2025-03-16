import json
from rest_framework.test import APITestCase
from rest_framework import status
from wallets.models import Wallet

class WalletTests(APITestCase):
    def setUp(self):
        # Create an initial wallet for retrieval and deletion tests.
        self.wallet = Wallet.objects.create(label="API Wallet")

    def test_create_and_retrieve_wallet(self):
        # Create a new wallet.
        url = "/api/wallets/"
        create_data = {
            "data": {
                "type": "Wallets",
                "attributes": {
                    "label": "New Wallet"
                }
            }
        }
        payload = json.dumps(create_data)
        create_response = self.client.post(url, payload, content_type='application/vnd.api+json')
        self.assertEqual(create_response.status_code, status.HTTP_201_CREATED,
                         msg=f"Create wallet failed: {create_response.content}")
        response_data = json.loads(create_response.content)
        new_wallet_id =  response_data["data"]["id"]

        # Retrieve the newly created wallet.
        retrieve_url = f"/api/wallets/{new_wallet_id}/"
        retrieve_response = self.client.get(retrieve_url, HTTP_ACCEPT='application/vnd.api+json')
        response_data = json.loads(retrieve_response.content)
        self.assertEqual(retrieve_response.status_code, status.HTTP_200_OK,
                         msg=f"Retrieve wallet failed: {retrieve_response.content}")
        self.assertEqual(response_data["data"]["attributes"]["label"], "New Wallet",
                         msg=f"Wallet label mismatch: {retrieve_response.content}")

    def test_delete_wallet(self):
        # Delete the wallet created in setUp.
        url = f"/api/wallets/{self.wallet.id}/"
        response = self.client.delete(url, HTTP_ACCEPT='application/vnd.api+json')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT,
                         msg=f"Delete wallet failed: {response.content}")
        self.assertFalse(Wallet.objects.filter(id=self.wallet.id).exists(),
                         msg=f"Wallet still exists after deletion: {response.content}")


class TransactionTests(APITestCase):
    def setUp(self):
        # Create a fresh wallet and an initial deposit of 100.00.
        self.wallet = Wallet.objects.create(label="Transaction Wallet")
        deposit_data = {
            "data": {
                "type": "Transactions",
                "attributes": {
                    "txid": "tx100",
                    "amount": "100.00"
                },
                "relationships": {
                    "wallet": {
                        "data": {"type": "Wallets", "id": str(self.wallet.id)}
                    }
                }
            }
        }
        payload = json.dumps(deposit_data)
        response = self.client.post("/api/transactions/", payload, content_type='application/vnd.api+json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED,
                         msg=f"Initial deposit failed: {response.content}")

    def test_create_deposit_transaction(self):
        # Create a deposit transaction of 50.00.
        url = "/api/transactions/"
        deposit_data = {
            "data": {
                "type": "Transactions",
                "attributes": {
                    "txid": "tx101",
                    "amount": "50.00"
                },
                "relationships": {
                    "wallet": {
                        "data": {"type": "Wallets", "id": str(self.wallet.id)}
                    }
                }
            }
        }
        payload = json.dumps(deposit_data)
        response = self.client.post(url, payload, content_type='application/vnd.api+json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED,
                         msg=f"Create deposit transaction failed: {response.content}")
        # Expected wallet balance: initial 100.00 + 50.00 = 150.00.
        self.wallet.refresh_from_db()
        self.assertEqual(float(self.wallet.balance), 150.00,
                         msg=f"Unexpected wallet balance: {response.content}")

    def test_withdraw_transaction_invalid(self):
        # Attempt to withdraw 200.00 from a wallet with a balance of 100.00.
        url = "/api/transactions/"
        withdraw_data = {
            "data": {
                "type": "Transactions",
                "attributes": {
                    "txid": "tx102",
                    "amount": "-200.00"
                },
                "relationships": {
                    "wallet": {
                        "data": {"type": "Wallets", "id": str(self.wallet.id)}
                    }
                }
            }
        }
        payload = json.dumps(withdraw_data)
        response = self.client.post(url, payload, content_type='application/vnd.api+json')
        # Expect a 400 error because the withdrawal would make the balance negative.
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST,
                         msg=f"Expected 400 error on invalid withdrawal: {response.content}")
        # The wallet balance should remain unchanged.
        self.wallet.refresh_from_db()
        self.assertEqual(float(self.wallet.balance), 100.00,
                         msg=f"Wallet balance changed unexpectedly: {response.content}")
