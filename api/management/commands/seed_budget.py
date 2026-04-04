import random
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from faker import Faker
from api.Bot.model import Bot
from api.Budget.model import Budget

fake = Faker()
User = get_user_model()


class Command(BaseCommand):
    help = 'Seed Budget records'

    def add_arguments(self, parser):
        parser.add_argument('count', type=int)

    def handle(self, *args, **options):
        n = options['count']
        users = list(User.objects.all())
        bots = list(Bot.objects.all())
        if not users:
            self.stdout.write(self.style.ERROR('No users found. Create a user first.'))
            return
        for _ in range(n):
            allocated = round(random.uniform(100, 5000), 2)
            consumed = round(random.uniform(0, allocated), 2)
            period_start = fake.date_this_year()
            Budget.objects.create(
                user=random.choice(users),
                bot=random.choice(bots) if bots else None,
                allocated_amount=allocated,
                consumed_amount=consumed,
                period_start=period_start,
                period_end=fake.date_between(start_date=period_start),
            )
        self.stdout.write(self.style.SUCCESS(f'Created {n} Budget records'))
