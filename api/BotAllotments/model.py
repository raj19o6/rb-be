import uuid
from django.db import models
from django.conf import settings
from api.Bot.model import Bot


class BotAllotments(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    bot = models.ForeignKey(Bot, on_delete=models.CASCADE, related_name='allotments')
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='bot_allotments'
    )
    allotted_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, null=True, blank=True,
        on_delete=models.SET_NULL, related_name='allotments_given'
    )
    allotted_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'api_bot_allotments'
        unique_together = ('bot', 'user')

    def __str__(self):
        return f"{self.bot.name} → {self.user.username}"
