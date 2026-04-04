import uuid
from django.db import models
from django.conf import settings
from api.Billing.model import Billing
from api.Payment.validators import validate_positive_amount


class Payment(models.Model):
    METHOD_CHOICES = [
        ('card', 'Card'),
        ('bank_transfer', 'Bank Transfer'),
        ('cash', 'Cash'),
        ('online', 'Online'),
    ]
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('refunded', 'Refunded'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    billing = models.ForeignKey(Billing, on_delete=models.CASCADE, related_name='payments')
    paid_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='payments'
    )
    amount = models.DecimalField(
        max_digits=10, decimal_places=2, validators=[validate_positive_amount]
    )
    transaction_id = models.CharField(
        max_length=255, unique=True, blank=True
    )
    method = models.CharField(max_length=20, choices=METHOD_CHOICES, default='online')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    paid_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'api_payment'

    def save(self, *args, **kwargs):
        if not self.transaction_id:
            self.transaction_id = f"TXN-{uuid.uuid4().hex[:12].upper()}"
        if self.status == 'completed' and not self.paid_at:
            from django.utils import timezone
            self.paid_at = timezone.now()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Payment {self.transaction_id} - {self.paid_by.username} ({self.status})"
