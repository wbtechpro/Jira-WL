from django.db import models


class PeriodForDownloadModel(models.Model):
    days = models.IntegerField(null=True, blank=True)
    start_date = models.DateField(null=True, blank=True)

    class Meta:
        verbose_name_plural = '!  Период, за который необходимо загрузить ворклоги'
        app_label = 'client'
