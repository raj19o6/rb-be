import uuid
from django.db import models
from api.Bot.model import Bot


class BotFunctions(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    bot = models.ForeignKey(Bot, on_delete=models.CASCADE, related_name='functions')
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    function_key = models.CharField(max_length=100, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'api_bot_functions'

    def __str__(self):
        return f"{self.name} ({self.function_key})"
