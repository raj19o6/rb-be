import random
from django.core.management.base import BaseCommand
from faker import Faker
from api.Bot.model import Bot
from api.BotPrereq.model import BotPrereq

fake = Faker()


class Command(BaseCommand):
    help = 'Seed BotPrereq records'

    def add_arguments(self, parser):
        parser.add_argument('count', type=int)

    def handle(self, *args, **options):
        n = options['count']
        bots = list(Bot.objects.all())
        if not bots:
            self.stdout.write(self.style.ERROR('No bots found. Run seed_bot first.'))
            return
        for _ in range(n):
            BotPrereq.objects.create(
                bot=random.choice(bots),
                name=fake.word().capitalize(),
                description=fake.sentence(),
                is_required=random.choice([True, False]),
            )
        self.stdout.write(self.style.SUCCESS(f'Created {n} BotPrereq records'))
