from main.models import Configs
from django.core.management.base import BaseCommand, CommandError
import subprocess


class Command(BaseCommand):
    help = 'Проверка статуса демона'

    def handle(self, *args, **options):
        if not Configs.objects.filter(pk=1).exists():  # если есть, то редактируем
            configs = Configs()
        else:
            configs = Configs.objects.get(pk=1)
        proc_status = subprocess.Popen(['systemctl status simple-waf | grep active | cut -d";" -f1'],
                                       stdout=subprocess.PIPE,
                                       shell=True)
        configs.daemon_status = proc_status.communicate()[0].decode("utf-8")
        configs.save()
        self.stdout.write(self.style.SUCCESS(configs.daemon_status))
