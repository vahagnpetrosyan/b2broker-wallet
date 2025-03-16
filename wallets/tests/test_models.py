from django.test import TestCase
from django.core.exceptions import ValidationError
from wallets.models import Wallet, Transaction


class WalletModelTests(TestCase):
    def setUp(self):
        self.wallet = Wallet.objects.create(label="Test Wallet")

    def test_deposit_and_withdrawal(self):
        # Deposit 100 units
        tx1 = Transaction.objects.create(wallet=self.wallet, txid="TX001", amount=100)
        self.wallet.refresh_from_db()
        self.assertEqual(self.wallet.balance, 100)

        # Withdraw 30 units
        tx2 = Transaction.objects.create(wallet=self.wallet, txid="TX002", amount=-30)
        self.wallet.refresh_from_db()
        self.assertEqual(self.wallet.balance, 70)  # 100 - 30

    def test_prevent_negative_balance(self):
        # Attempt to withdraw more than the wallet's balance should raise an error
        with self.assertRaises(ValidationError):
            Transaction.objects.create(wallet=self.wallet, txid="TXNEG", amount=-50)
        self.wallet.refresh_from_db()
        self.assertEqual(self.wallet.balance, 0)

    def test_transaction_txid_unique(self):
        Transaction.objects.create(wallet=self.wallet, txid="TXDUPE", amount=10)
        with self.assertRaises(Exception):
            Transaction.objects.create(wallet=self.wallet, txid="TXDUPE", amount=20)


class TransactionModelTests(TestCase):
    def setUp(self):
        self.wallet1 = Wallet.objects.create(label="Wallet1")
        self.wallet2 = Wallet.objects.create(label="Wallet2")

    def test_transfer_between_wallets(self):
        # Create a transaction on wallet1
        tx = Transaction.objects.create(wallet=self.wallet1, txid="TXMOVE", amount=50)
        self.wallet1.refresh_from_db()
        self.assertEqual(self.wallet1.balance, 50)

        # Move the transaction to wallet2
        tx.wallet = self.wallet2
        tx.save()
        self.wallet1.refresh_from_db()
        self.wallet2.refresh_from_db()
        self.assertEqual(self.wallet1.balance, 0)
        self.assertEqual(self.wallet2.balance, 50)
