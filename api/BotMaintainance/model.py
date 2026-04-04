import uuid
from django.db import models
from django.conf import settings
from api.Bot.model import Bot


class BotMaintainance(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    bot = models.ForeignKey(Bot, on_delete=models.CASCADE, related_name='maintenance_records')
    reason = models.TextField()
    started_at = models.DateTimeField()
    ended_at = models.DateTimeField(null=True, blank=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='bot_maintenance'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'api_bot_maintainance'

    def __str__(self):
        return f"Maintenance for {self.bot.name} at {self.started_at}"
