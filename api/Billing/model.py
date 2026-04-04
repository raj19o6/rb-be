import uuid
from django.db import models
from django.conf import settings
from api.Bot.model import Bot


class Billing(models.Model):
    STATUS_CHOICES = [
        ('unpaid', 'Unpaid'),
        ('paid', 'Paid'),
        ('overdue', 'Overdue'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='billings'
    )
    bot = models.ForeignKey(Bot, null=True, blank=True, on_delete=models.SET_NULL, related_name='billings')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='unpaid')
    billing_date = models.DateField()
    due_date = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'api_billing'

    def __str__(self):
        return f"Billing {self.id} - {self.user.username} ({self.status})"
