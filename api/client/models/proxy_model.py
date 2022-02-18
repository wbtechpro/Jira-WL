from django.db import models


class ProxyModel(models.Model):
    class Meta:
        verbose_name_plural = '! Количество дней, за которые необходимо загрузить ворклоги'
        app_label = 'client'
