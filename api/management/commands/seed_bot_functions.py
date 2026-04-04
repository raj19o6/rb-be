import random
from django.core.management.base import BaseCommand
from faker import Faker
from api.Bot.model import Bot
from api.BotFunctions.model import BotFunctions

fake = Faker()


class Command(BaseCommand):
    help = 'Seed BotFunctions records'

    def add_arguments(self, parser):
        parser.add_argument('count', type=int)

    def handle(self, *args, **options):
        n = options['count']
        bots = list(Bot.objects.all())
        if not bots:
            self.stdout.write(self.style.ERROR('No bots found. Run seed_bot first.'))
            return
        for _ in range(n):
            BotFunctions.objects.create(
                bot=random.choice(bots),
                name=fake.word().capitalize() + ' Function',
                description=fake.sentence(),
                function_key=fake.unique.slug(),
            )
        self.stdout.write(self.style.SUCCESS(f'Created {n} BotFunctions records'))
