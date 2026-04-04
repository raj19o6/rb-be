import random
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from api.Bot.model import Bot
from api.BotAllotments.model import BotAllotments

User = get_user_model()


class Command(BaseCommand):
    help = 'Seed BotAllotments records'

    def add_arguments(self, parser):
        parser.add_argument('count', type=int)

    def handle(self, *args, **options):
        n = options['count']
        bots = list(Bot.objects.all())
        users = list(User.objects.all())
        if not bots or not users:
            self.stdout.write(self.style.ERROR('No bots or users found. Run seed_bot first.'))
            return
        created = 0
        attempts = 0
        while created < n and attempts < n * 5:
            attempts += 1
            try:
                BotAllotments.objects.create(
                    bot=random.choice(bots),
                    user=random.choice(users),
                    allotted_by=random.choice(users),
                )
                created += 1
            except Exception:
                continue
        self.stdout.write(self.style.SUCCESS(f'Created {created} BotAllotments records'))
