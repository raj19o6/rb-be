import random
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from faker import Faker
from api.Bot.model import Bot

fake = Faker()
User = get_user_model()


class Command(BaseCommand):
    help = 'Seed Bot records'

    def add_arguments(self, parser):
        parser.add_argument('count', type=int)

    def handle(self, *args, **options):
        n = options['count']
        users = list(User.objects.all())
        if not users:
            self.stdout.write(self.style.ERROR('No users found. Create a user first.'))
            return
        for _ in range(n):
            Bot.objects.create(
                name=fake.unique.word().capitalize() + 'Bot',
                description=fake.sentence(),
                status=random.choice(['active', 'inactive', 'maintenance']),
                created_by=random.choice(users),
            )
        self.stdout.write(self.style.SUCCESS(f'Created {n} Bot records'))
