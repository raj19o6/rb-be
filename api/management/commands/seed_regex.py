import random
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from faker import Faker
from api.Regex.model import Regex

fake = Faker()
User = get_user_model()

SAMPLE_PATTERNS = [
    r'^\d{10}$',
    r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$',
    r'^\d{4}-\d{2}-\d{2}$',
    r'^[A-Z]{2}\d{6}$',
    r'^\+?[1-9]\d{1,14}$',
]


class Command(BaseCommand):
    help = 'Seed Regex records'

    def add_arguments(self, parser):
        parser.add_argument('count', type=int)

    def handle(self, *args, **options):
        n = options['count']
        users = list(User.objects.all())
        if not users:
            self.stdout.write(self.style.ERROR('No users found. Create a user first.'))
            return
        for _ in range(n):
            Regex.objects.create(
                name=fake.unique.word().capitalize() + ' Pattern',
                pattern=random.choice(SAMPLE_PATTERNS),
                description=fake.sentence(),
                created_by=random.choice(users),
            )
        self.stdout.write(self.style.SUCCESS(f'Created {n} Regex records'))
