from main.models import Configs
from django.core.management.base import BaseCommand, CommandError


class Command(BaseCommand):
    help = 'Предварительная настройка системы'

    def add_arguments(self, parser):
        parser.add_argument('hostname', type=str)
        parser.add_argument('port', type=int)
        parser.add_argument("https",
                            default=False,
                            nargs="?",
                            help="Activate https")

    def handle(self, *args, **options):
        if options['hostname'] and options['port'] and options['https'] is not None:
            if not Configs.objects.filter(pk=1).exists():  # если есть, то редактируем
                configs = Configs()
            else:
                configs = Configs.objects.get(pk=1)
            configs.hostname = options['hostname']
            configs.port = options['port']
            configs.https = options['https']
            configs.save()
        else:
            raise CommandError('Не переданы необходимые параметры')

        self.stdout.write(self.style.SUCCESS('Готово!'))
