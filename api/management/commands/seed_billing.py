import random
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from faker import Faker
from api.Bot.model import Bot
from api.Billing.model import Billing

fake = Faker()
User = get_user_model()


class Command(BaseCommand):
    help = 'Seed Billing records'

    def add_arguments(self, parser):
        parser.add_argument('count', type=int)

    def handle(self, *args, **options):
        n = options['count']
        users = list(User.objects.all())
        bots = list(Bot.objects.all())
        if not users:
            self.stdout.write(self.style.ERROR('No users found. Create a user first.'))
            return
        statuses = [s[0] for s in Billing.STATUS_CHOICES]
        for _ in range(n):
            billing_date = fake.date_this_year()
            Billing.objects.create(
                user=random.choice(users),
                bot=random.choice(bots) if bots else None,
                amount=round(random.uniform(10, 1000), 2),
                status=random.choice(statuses),
                billing_date=billing_date,
                due_date=fake.date_between(start_date=billing_date),
            )
        self.stdout.write(self.style.SUCCESS(f'Created {n} Billing records'))
