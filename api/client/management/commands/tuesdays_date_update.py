from django.core.management.base import BaseCommand
from datetime import datetime

from client.models import PeriodForDownloadModel


class Command(BaseCommand):
    """
    Обновляет конечную дату для промежуточного (раз в неделю ночью с понедельника на вторник) скачивания ворклогов:
    ставит такой датой текущую, если в этот день вторник.
    Количество дней для скачивания ворклогов - 90. Его можно будет в любой момент поменять в админке
    """

    def handle(self, *args, **options):
        today = datetime.today()
        day_of_week = today.weekday()
        if day_of_week == 1 and today.day != 28:
            model_instance = PeriodForDownloadModel.objects.get(pk=1)
            model_instance.end_date = today
            model_instance.days = 90
            model_instance.save()
        else:
            return
