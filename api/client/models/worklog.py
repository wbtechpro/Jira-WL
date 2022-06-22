from django.db import models

from client.models.issue import IssuesInfo


class WorklogQuerySet(models.QuerySet):

    def group_worklogs_by_agreed_orders(self):
        """
        Groups by tasks belonging to orders and counts total worklogs
        """
        query = self.values(
            # 'issue__agreed_order_key',
            'issue__key',
            'issue__project',
            'issue__agreed_order_finolog__finolog_id',
            # 'issue__agreed_order_finolog__jira_key',
        ).annotate(
            logged_time=models.Sum('time_spent_seconds')
        ).order_by()
        return query

    def by_jira_account_id(self, account_id):
        return self.filter(account_id=account_id)


class WorklogWithInfo(models.Model):

    json_data = models.JSONField()
    url = models.URLField(verbose_name='ссылка на ворклог')
    display_name = models.CharField(verbose_name='displayName', max_length=50)
    account_id = models.CharField(verbose_name='accountId', max_length=50)
    created = models.DateTimeField(verbose_name='created')
    updated = models.DateTimeField(verbose_name='updated')
    started = models.DateTimeField(verbose_name='started')
    time_spent_seconds = models.IntegerField(verbose_name='timeSpentSeconds')
    time_spent = models.CharField(verbose_name='timeSpent', max_length=50)
    jira_id = models.CharField(verbose_name='worklog jira id', max_length=50)
    issueId = models.CharField(verbose_name='issueId', max_length=50)
    issue = models.ForeignKey(
        IssuesInfo, verbose_name='Таск, связанный по issueId', related_name='worklogs', on_delete=models.DO_NOTHING,
        blank=True, null=True)

    objects = WorklogQuerySet.as_manager()

    class Meta:
        verbose_name = 'Ворклог'
        verbose_name_plural = 'Ворклоги'
        ordering = ('updated',)


    def __str__(self):
        return f'Ворклог с jira_id {self.jira_id}'

    def save(self, *args, **kwargs):
        """
        In the client, only json from Jira API is transmitted, and here separate fields are filled from json
        """
        self.display_name = self.json_data.get('author').get('displayName')
        self.url = self.json_data.get('self')
        self.account_id = self.json_data.get('author').get('accountId')
        self.created = self.json_data.get('created')
        self.updated = self.json_data.get('updated')
        self.started = self.json_data.get('started')
        self.time_spent_seconds = self.json_data.get('timeSpentSeconds')
        self.time_spent = self.json_data.get('timeSpent')
        self.jira_id = self.json_data.get('id')
        self.issueId = self.json_data.get('issueId')

        self.issue = IssuesInfo.objects.filter(jira_id=self.issueId).first() or None

        return super().save(*args, **kwargs)
