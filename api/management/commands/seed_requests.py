import random
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from faker import Faker
from api.Requests.model import Requests

fake = Faker()
User = get_user_model()


class Command(BaseCommand):
    help = 'Seed Requests records'

    def add_arguments(self, parser):
        parser.add_argument('count', type=int)

    def handle(self, *args, **options):
        n = options['count']
        users = list(User.objects.all())
        if not users:
            self.stdout.write(self.style.ERROR('No users found. Create a user first.'))
            return
        statuses = [s[0] for s in Requests.STATUS_CHOICES]
        for _ in range(n):
            Requests.objects.create(
                title=fake.sentence(nb_words=4),
                description=fake.paragraph(),
                status=random.choice(statuses),
                requested_by=random.choice(users),
                assigned_to=random.choice(users),
            )
        self.stdout.write(self.style.SUCCESS(f'Created {n} Requests records'))
