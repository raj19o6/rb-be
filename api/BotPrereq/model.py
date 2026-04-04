import uuid
from django.db import models
from api.Bot.model import Bot


class BotPrereq(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    bot = models.ForeignKey(Bot, on_delete=models.CASCADE, related_name='prerequisites')
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    is_required = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'api_bot_prereq'

    def __str__(self):
        return f"{self.name} (prereq for {self.bot.name})"
