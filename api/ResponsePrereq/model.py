import uuid
from django.db import models
from django.conf import settings
from api.Bot.model import Bot


class ResponsePrereq(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    bot = models.ForeignKey(Bot, on_delete=models.CASCADE, related_name='response_prereqs')
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='response_prereqs'
    )
    key = models.CharField(max_length=255)
    value = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'api_response_prereq'
        unique_together = ('bot', 'user', 'key')

    def __str__(self):
        return f"{self.key} for {self.user.username} on {self.bot.name}"
