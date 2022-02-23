from django.db import models


class DaysForDownloadModel(models.Model):
    days = models.IntegerField(null=True, blank=True)

    class Meta:
        verbose_name_plural = '! Количество дней, за которые необходимо загрузить ворклоги'
        app_label = 'client'
