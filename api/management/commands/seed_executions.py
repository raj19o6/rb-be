import random
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.utils import timezone
from faker import Faker
from api.Bot.model import Bot
from api.Requests.model import Requests
from api.Executions.model import Executions

fake = Faker()
User = get_user_model()


class Command(BaseCommand):
    help = 'Seed Executions records'

    def add_arguments(self, parser):
        parser.add_argument('count', type=int)

    def handle(self, *args, **options):
        n = options['count']
        bots = list(Bot.objects.all())
        users = list(User.objects.all())
        requests_qs = list(Requests.objects.all())
        if not bots or not users:
            self.stdout.write(self.style.ERROR('No bots or users found. Run seed_bot and seed_requests first.'))
            return
        statuses = [s[0] for s in Executions.STATUS_CHOICES]
        for _ in range(n):
            started = fake.date_time_this_year(tzinfo=timezone.utc)
            Executions.objects.create(
                bot=random.choice(bots),
                request=random.choice(requests_qs) if requests_qs else None,
                executed_by=random.choice(users),
                status=random.choice(statuses),
                started_at=started,
                ended_at=fake.date_time_between(start_date=started, tzinfo=timezone.utc),
            )
        self.stdout.write(self.style.SUCCESS(f'Created {n} Executions records'))
