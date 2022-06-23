from json import dumps, loads

from client.models.worklog import *
from .test_models_setup import WorklogWithInfoTestsSetUp


class IssueModelTest(WorklogWithInfoTestsSetUp):

    def test_worklog_queryset_returns_grouped_by_orders_tasks_and_logged_time(self):
        """
        Checks if the WorklogQuerySet manager actually returns data from the WorklogWithInfo model, grouped by tasks
        belonging to orders, and calculates the total time spent by worklogs
        """
        model_data = WorklogWithInfo.objects.values('issue__key', 'issue__project',
                                                    'issue__agreed_order_finolog__finolog_id', ) \
            .annotate(logged_time=models.Sum('time_spent_seconds')).order_by()
        test_instances = WorklogWithInfo.objects.group_worklogs_by_agreed_orders()
        self.assertQuerysetEqual(model_data, test_instances)

    def test_worklogs_filtered_by_account_id(self):
        """
        Checks if the by_jira_account_id function actually filters worklogs by user id.
        For the test, one user worklog with id 0 and two user worklogs with id 1 have been added to the database
        """
        model_data_0 = WorklogWithInfo.objects.filter(account_id='0')
        model_data_1 = WorklogWithInfo.objects.filter(account_id='1')
        test_instances_0 = WorklogWithInfo.objects.by_jira_account_id('0')
        test_instances_1 = WorklogWithInfo.objects.by_jira_account_id('1')
        self.assertEqual(len(model_data_0), 1)
        self.assertEqual(len(model_data_1), 2)
        self.assertQuerysetEqual(model_data_0, test_instances_0)
        self.assertQuerysetEqual(model_data_1, test_instances_1)

    def test_string_worklog_id_representation(self):
        """
        Checks the work of the __str__ method, which should return the id of the worklog
        """
        model_data = WorklogWithInfo.objects.all().first()
        self.assertEqual(model_data.__str__(), 'Ворклог с jira_id 00')

    #
    def test_save_data_from_json(self):
        """
        Tests the work of the overridden save method, which takes data for the model from JSON received from the Jira
        API
        """
        instance_json_data = loads(dumps({"author": {"displayName": "Random Randomovich", "accountId": "0"},
                                          "self": "random.url/three", "created": "2022-01-01 10:00:00",
                                          "updated": "2022-01-01 10:00:00", "started": "2022-01-01 09:00:00",
                                          "timeSpentSeconds": 3600, "timeSpent": "1h", "id": '03', "issueId": '03'}))
        WorklogWithInfo(json_data=instance_json_data).save()
        instance_data = WorklogWithInfo.objects.get(pk=len(WorklogWithInfo.objects.all()))
        self.assertEqual(instance_data.display_name, 'Random Randomovich')
        self.assertEqual(instance_data.url, 'random.url/three')
        self.assertEqual(instance_data.account_id, '0')
        self.assertEqual(str(instance_data.created), '2022-01-01 10:00:00+00:00')
        self.assertEqual(str(instance_data.updated), '2022-01-01 10:00:00+00:00')
        self.assertEqual(str(instance_data.started), '2022-01-01 09:00:00+00:00')
        self.assertEqual(instance_data.time_spent_seconds, 3600)
        self.assertEqual(instance_data.time_spent, '1h')
        self.assertEqual(instance_data.jira_id, '03')
        self.assertEqual(instance_data.issueId, '03')
