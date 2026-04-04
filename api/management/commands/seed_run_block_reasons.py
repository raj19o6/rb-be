import random
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from faker import Faker
from api.Bot.model import Bot
from api.RunBlockReasons.model import RunBlockReasons

fake = Faker()
User = get_user_model()


class Command(BaseCommand):
    help = 'Seed RunBlockReasons records'

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
            RunBlockReasons.objects.create(
                bot=random.choice(bots),
                user=random.choice(users),
                reason=fake.sentence(),
                is_active=random.choice([True, False]),
                created_by=random.choice(users),
            )
        self.stdout.write(self.style.SUCCESS(f'Created {n} RunBlockReasons records'))
