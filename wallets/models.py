from django.db import models, transaction as db_transaction
from django.core.exceptions import ValidationError

class Wallet(models.Model):
    label = models.CharField(max_length=100)
    balance = models.DecimalField(max_digits=36, decimal_places=18, default=0)

    class Meta:
        indexes = [
            models.Index(fields=['label']),  # Index on label for faster lookups or sorting by label
        ]

    def __str__(self):
        return f"{self.label} (Balance: {self.balance})"


class Transaction(models.Model):
    wallet = models.ForeignKey(Wallet, related_name='transactions', on_delete=models.CASCADE)
    txid = models.CharField(max_length=255, unique=True)
    amount = models.DecimalField(max_digits=36, decimal_places=18)

    class Meta:
        indexes = [
            models.Index(fields=['wallet']),    # Index to quickly filter transactions by wallet
            models.Index(fields=['txid']),      # Unique index
        ]

    def save(self, *args, **kwargs):
        """
        Override save to ensure wallet balance consistency:
        - Add this transaction amount to the wallet's balance.
        - Prevent negative balance by validating before commit.
        """
        with db_transaction.atomic():
            # If updating an existing transaction, get the original record for difference calculation
            old_amount = None
            old_wallet_id = None
            if self.pk:
                original = Transaction.objects.select_for_update().get(pk=self.pk)
                old_amount = original.amount
                old_wallet_id = original.wallet_id

            # Lock the involved wallet(s) to prevent concurrent modifications
            wallet = Wallet.objects.select_for_update().get(pk=self.wallet_id)
            if old_wallet_id and old_wallet_id != self.wallet_id:
                # Also lock the original wallet if transferring between wallets (unlikely in typical use)
                original_wallet = Wallet.objects.select_for_update().get(pk=old_wallet_id)
            else:
                original_wallet = None

            # Calculate new balances
            if old_amount is not None:
                # Existing transaction is being updated
                if original_wallet and original_wallet.pk != wallet.pk:
                    # Transaction’s wallet changed to a different wallet
                    original_new_balance = original_wallet.balance - old_amount
                    new_wallet_balance = wallet.balance + self.amount
                    if original_new_balance < 0:
                        raise ValidationError("Original wallet balance cannot go negative.")
                    original_wallet.balance = original_new_balance
                    original_wallet.save()
                else:
                    # Same wallet, adjust by difference
                    new_wallet_balance = wallet.balance - old_amount + self.amount
            else:
                # New transaction
                new_wallet_balance = wallet.balance + self.amount

            # Validate non-negative balance
            if new_wallet_balance < 0:
                raise ValidationError("Wallet balance cannot be negative.")

            # Update wallet balance and save transaction
            wallet.balance = new_wallet_balance
            wallet.save()
            super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        """Override delete to adjust the wallet balance accordingly and prevent negative result."""
        with db_transaction.atomic():
            wallet = Wallet.objects.select_for_update().get(pk=self.wallet_id)
            new_balance = wallet.balance - self.amount
            if new_balance < 0:
                raise ValidationError("Cannot delete transaction: wallet balance would become negative.")
            wallet.balance = new_balance
            wallet.save()
            super().delete(*args, **kwargs)
