from django.core.management.base import BaseCommand
from MainApp.models import User

class Command(BaseCommand):
    help = "Отображает зарегистрированных пользователей"
    def add_arguments(self, parser):
        parser.add_argument(
            '--verbose',  # Имя опции
            action='store_true',  # Тип действия: просто флаг, который устанавливается в True при наличии
            help='Вывести более подробную информацию о пользователях.',
        )
        parser.add_argument(
            '--limit',
            type=int,  # Указываем, что аргумент должен быть целым числом
            help='Ограничить количество выводимых пользователей.',
        )

    def handle(self, *args, **options):
        verbose = options['verbose']
        limit = options['limit']
        users = User.objects.all()

        for user in users[:limit]:
            if verbose:
                self.stdout.write(f"[{user.id}]User:{user.username} email:{user.email}")
            else:
                self.stdout.write(f"[{user.id}]User:{user.username}")