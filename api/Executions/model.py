import uuid
from django.db import models
from django.conf import settings
from api.Bot.model import Bot
from api.Requests.model import Requests


class Executions(models.Model):
    STATUS_CHOICES = [
        ('queued', 'Queued'),
        ('running', 'Running'),
        ('success', 'Success'),
        ('failed', 'Failed'),
        ('cancelled', 'Cancelled'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    bot = models.ForeignKey(Bot, on_delete=models.CASCADE, related_name='executions')
    request = models.ForeignKey(
        Requests, null=True, blank=True, on_delete=models.SET_NULL, related_name='executions'
    )
    executed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='executions'
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='queued')
    failure_reason = models.TextField(blank=True, null=True)
    started_at = models.DateTimeField(null=True, blank=True)
    ended_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'api_executions'

    def __str__(self):
        return f"Execution {self.id} - {self.bot.name} ({self.status})"
