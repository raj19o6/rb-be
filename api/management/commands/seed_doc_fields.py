import random
from django.core.management.base import BaseCommand
from faker import Faker
from api.DocCategory.model import DocCategory
from api.DocFields.model import DocFields

fake = Faker()


class Command(BaseCommand):
    help = 'Seed DocFields records'

    def add_arguments(self, parser):
        parser.add_argument('count', type=int)

    def handle(self, *args, **options):
        n = options['count']
        categories = list(DocCategory.objects.all())
        if not categories:
            self.stdout.write(self.style.ERROR('No categories found. Run seed_doc_category first.'))
            return
        field_types = [f[0] for f in DocFields.FIELD_TYPE_CHOICES]
        for _ in range(n):
            DocFields.objects.create(
                category=random.choice(categories),
                name=fake.word().capitalize() + ' Field',
                field_type=random.choice(field_types),
                is_required=random.choice([True, False]),
            )
        self.stdout.write(self.style.SUCCESS(f'Created {n} DocFields records'))
