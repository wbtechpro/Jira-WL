from django.db import models


class IssueQuerySet(models.QuerySet):

    def unique_agreed_keys(self):
        return self.values('agreed_order_key').distinct()


class IssuesInfo(models.Model):

    NOT_AGREED_ORDER = 'not_agreed_order'

    json_data = models.JSONField()
    url = models.URLField(verbose_name='ссылка на таск')
    summary = models.TextField(verbose_name='summary')
    project = models.CharField(verbose_name='project', max_length=50)
    key = models.CharField(verbose_name='key', max_length=50)
    jira_id = models.IntegerField(verbose_name='issue jira id')
    agreed_order_key = models.CharField(
        verbose_name='Ключ заказа (если относится к заказу)', blank=True, null=True, max_length=50)
    agreed_order_finolog = models.ForeignKey('FinologOrder', blank=True, null=True, on_delete=models.SET_NULL)

    objects = IssueQuerySet.as_manager()

    class Meta:
        verbose_name = 'таск'
        verbose_name_plural = 'таски'

    def __str__(self):
        return f'{self.key}'

    def save(self, *args, **kwargs):
        """
        In the client, only json from Jira API is transmitted, and here separate fields are filled from json
        """
        self.url = self.json_data.get('self')
        self.summary = self.json_data.get('fields').get('summary')
        self.project = self.json_data.get('key').split('-')[0]
        self.key = self.json_data.get('key')
        self.jira_id = self.json_data.get('id')
        self.agreed_order_key = self._get_agreed_order_key()
        return super().save(*args, **kwargs)

    @property
    def is_agreed_order(self):
        """
        Order agreed by the customer
        The agreed order has a special field "send to Finolog"
        """
        if x := self.json_data.get('fields').get('customfield_10376'):
            # Returns "Submit" - i.e. the task must be sent to Finolog as agreed
            return bool(x[0].get('value'))
        return False

    def _get_agreed_order_key(self):
        """
        Returns the index of the parent matched order, or its own if the task itself is a matched order
        """
        if self.is_agreed_order:
            return self.key
        return self.json_data.get('fields').get('customfield_10100') or self.NOT_AGREED_ORDER
