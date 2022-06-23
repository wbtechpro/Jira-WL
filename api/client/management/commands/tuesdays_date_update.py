from django.core.management.base import BaseCommand
from datetime import datetime

from client.models import PeriodForDownloadModel


class Command(BaseCommand):
    """
    Updates the end date for the intermediate (once a week at night from Monday to Tuesday) download of worklogs:
    sets this date to the current one if that day is Tuesday.
    The number of days for downloading worklogs is 90. It can be changed at any time in the admin panel
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
