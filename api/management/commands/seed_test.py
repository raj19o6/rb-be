import random
from django.core.management.base import BaseCommand
from faker import Faker
from api.Address.model import Address
from api.TestAPI.model import Test

fake = Faker()


class Command(BaseCommand):
    help = 'Seed Test records'

    def add_arguments(self, parser):
        parser.add_argument('count', type=int)

    def handle(self, *args, **options):
        n = options['count']
        addresses = list(Address.objects.all())
        if not addresses:
            self.stdout.write(self.style.ERROR('No Address records found. Run seed_address first.'))
            return
        for _ in range(n):
            Test.objects.create(
                name=fake.word(),
                description=fake.sentence(),
                address=random.choice(addresses),
            )
        self.stdout.write(self.style.SUCCESS(f'Created {n} Test records'))
