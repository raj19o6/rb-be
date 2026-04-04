import uuid
from django.db import models
from django.conf import settings
from api.Bot.model import Bot


class Credentials(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    bot = models.ForeignKey(Bot, on_delete=models.CASCADE, related_name='credentials')
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='credentials'
    )
    username = models.CharField(max_length=255)
    password = models.CharField(max_length=255)
    extra_data = models.JSONField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'api_credentials'

    def __str__(self):
        return f"Credentials for {self.user.username} on {self.bot.name}"
