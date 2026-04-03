from django.core.management.base import BaseCommand
from faker import Faker
from api.Address.model import Address

fake = Faker()


class Command(BaseCommand):
    help = 'Seed Address records'

    def add_arguments(self, parser):
        parser.add_argument('count', type=int)

    def handle(self, *args, **options):
        n = options['count']
        for _ in range(n):
            Address.objects.create(
                address=fake.street_address(),
                city=fake.city(),
                state=fake.state(),
                pincode=int(fake.postcode()[:6].replace('-', '0').ljust(6, '0')),
            )
        self.stdout.write(self.style.SUCCESS(f'Created {n} Address records'))
