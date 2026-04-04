import random
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from faker import Faker
from api.Bot.model import Bot
from api.Bugs.model import Bugs

fake = Faker()
User = get_user_model()


class Command(BaseCommand):
    help = 'Seed Bugs records'

    def add_arguments(self, parser):
        parser.add_argument('count', type=int)

    def handle(self, *args, **options):
        n = options['count']
        users = list(User.objects.all())
        bots = list(Bot.objects.all())
        if not users:
            self.stdout.write(self.style.ERROR('No users found. Create a user first.'))
            return
        severities = [s[0] for s in Bugs.SEVERITY_CHOICES]
        statuses = [s[0] for s in Bugs.STATUS_CHOICES]
        for _ in range(n):
            Bugs.objects.create(
                bot=random.choice(bots) if bots else None,
                title=fake.sentence(nb_words=5),
                description=fake.paragraph(),
                severity=random.choice(severities),
                status=random.choice(statuses),
                reported_by=random.choice(users),
                assigned_to=random.choice(users),
            )
        self.stdout.write(self.style.SUCCESS(f'Created {n} Bugs records'))
