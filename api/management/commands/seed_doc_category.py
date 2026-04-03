import random
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from faker import Faker
from api.DocCategory.model import DocCategory

fake = Faker()
User = get_user_model()


class Command(BaseCommand):
    help = 'Seed DocCategory records'

    def add_arguments(self, parser):
        parser.add_argument('count', type=int)

    def handle(self, *args, **options):
        n = options['count']
        users = list(User.objects.all())
        if not users:
            self.stdout.write(self.style.ERROR('No users found. Create a user first.'))
            return
        for _ in range(n):
            DocCategory.objects.create(
                name=fake.unique.word().capitalize() + ' Category',
                description=fake.sentence(),
                created_by=random.choice(users),
            )
        self.stdout.write(self.style.SUCCESS(f'Created {n} DocCategory records'))
