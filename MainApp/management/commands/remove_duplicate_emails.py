from django.core.management.base import BaseCommand
from MainApp.models import User, UserProfile

class Command(BaseCommand):
    help = '....'

    def handle(self, *args, **options):
        ...