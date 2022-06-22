from django.db import models

from client.models.issue import IssuesInfo


class FinologApiToken(models.Model):

    token = models.CharField(verbose_name='токен', max_length=150)

    class Meta:
        verbose_name = 'Токен Финолога'
        verbose_name_plural = 'Токены Финолога'


class FinologOrder(models.Model):

    """
    Model-correspondence to the task-order (issue) in Jira and order in Finolog
    """

    jira_key = models.CharField(max_length=50)
    finolog_id = models.CharField(max_length=50)

    class Meta:
        verbose_name = 'заказ в Финологе'
        verbose_name_plural = 'заказы в Финологе'

    def __str__(self):
        return f'Заказ в финологе {self.jira_key} -- {self.finolog_id}'

    @classmethod
    def save_from_jira_finolog_tuples(cls, jira_finololog_tiples):
        for jira_finolog in jira_finololog_tiples:
            jira_key = jira_finolog[0]
            finolog_id = jira_finolog[1]
            finolog_order = cls(jira_key=jira_key, finolog_id=finolog_id)
            finolog_order.save()
            issues = IssuesInfo.objects.filter(agreed_order_key=jira_key)
            issues.update(agreed_order_finolog=finolog_order)


class FinologProject(models.Model):

    """
    Model-correspondence to the project (issue) in Jira and order in Finolog
    118854: 'AREND',
    118959: 'BIOM',
    121411: 'BLOG',
    etc.
    There is a django command to load the default ones
    """

    jira_key = models.CharField(max_length=50, unique=True)
    finolog_id = models.CharField(max_length=50)
    category_id = models.CharField(max_length=250, blank=True, default='Статья расходов не указана')

    class Meta:
        verbose_name = 'проект в Финологе'
        verbose_name_plural = 'проекты в Финологе'

    def __str__(self):
        return f'Проект в финологе {self.jira_key} -- {self.finolog_id}'
