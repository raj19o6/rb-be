import random
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.utils import timezone
from faker import Faker
from api.Bot.model import Bot
from api.BotMaintainance.model import BotMaintainance

fake = Faker()
User = get_user_model()


class Command(BaseCommand):
    help = 'Seed BotMaintainance records'

    def add_arguments(self, parser):
        parser.add_argument('count', type=int)

    def handle(self, *args, **options):
        n = options['count']
        bots = list(Bot.objects.all())
        users = list(User.objects.all())
        if not bots or not users:
            self.stdout.write(self.style.ERROR('No bots or users found. Run seed_bot first.'))
            return
        for _ in range(n):
            started = fake.date_time_this_year(tzinfo=timezone.utc)
            BotMaintainance.objects.create(
                bot=random.choice(bots),
                reason=fake.sentence(),
                started_at=started,
                ended_at=fake.date_time_between(start_date=started, tzinfo=timezone.utc),
                created_by=random.choice(users),
            )
        self.stdout.write(self.style.SUCCESS(f'Created {n} BotMaintainance records'))
