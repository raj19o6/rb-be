import random
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from faker import Faker
from api.Notification.model import Notification

fake = Faker()
User = get_user_model()


class Command(BaseCommand):
    help = 'Seed Notification records'

    def add_arguments(self, parser):
        parser.add_argument('count', type=int)

    def handle(self, *args, **options):
        n = options['count']
        users = list(User.objects.all())
        if not users:
            self.stdout.write(self.style.ERROR('No users found. Create a user first.'))
            return
        types = [t[0] for t in Notification.TYPE_CHOICES]
        for _ in range(n):
            Notification.objects.create(
                user=random.choice(users),
                title=fake.sentence(nb_words=4),
                message=fake.paragraph(),
                notification_type=random.choice(types),
                is_read=random.choice([True, False]),
            )
        self.stdout.write(self.style.SUCCESS(f'Created {n} Notification records'))
