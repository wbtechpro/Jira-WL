from json import dumps, loads

from rest_framework.test import APITestCase

from client.models import IssuesInfo, WorklogWithInfo, FinologOrder, FinologProject


class ViewsAndSerializersTestSetUp(APITestCase):

    def setUp(self):
        # 1. ISSUES DATA

        # 1.1. URLs
        self.base_issues_view = 'https://jira-wl.wbtech.pro/jira-client-api/issues/'

        # 1.2. Model instances
        self.issue_data = loads(dumps({"self": "random.url/test",
                                       "fields": {"summary": "test", "customfield_10100": 'TEST-123'},
                                       "key": "test-123", "id": "01"}))
        IssuesInfo(json_data=self.issue_data).save()
        self.issue_data_for_filter_test_1 = loads(dumps({"self": "random.url/test_01",
                                                         "fields": {"summary": "test", "customfield_10100": 'TEST-123'},
                                                         "key": "test-123", "id": "02"}))
        IssuesInfo(json_data=self.issue_data_for_filter_test_1).save()
        self.issue_data_for_filter_test_2 = loads(dumps({"self": "random.url/test_02",
                                                         "fields": {"summary": "test", "customfield_10100": 'TEST-234'},
                                                         "key": "add_test-234", "id": "03"}))
        IssuesInfo(json_data=self.issue_data_for_filter_test_2).save()

        # 1.3. Model fields
        self.test_data_issue_fields = ['id', 'url', 'summary', 'project', 'key', 'jira_id', 'agreed_order_key',
                                       'agreed_order_finolog']

        # 2. WORKLOGS DATA

        # 2.1. URLs
        self.base_worklogs_view = 'https://jira-wl.wbtech.pro/jira-client-api/worklogs/'

        # 2.2. Model instances
        self.worklog_data = loads(dumps({"author": {"displayName": "Random Randomovich", "accountId": "0"},
                                         "self": "random.url/zero", "created": "2022-01-01 10:00:00",
                                         "updated": "2022-01-01 10:00:00", "started": "2022-01-01 09:00:00",
                                         "timeSpentSeconds": 3600, "timeSpent": "1h", "id": '00', "issueId": '00'}))
        WorklogWithInfo(json_data=self.worklog_data).save()
        self.worklog_data_for_filters_test_1 = loads(
            dumps({"author": {"displayName": "Random Randomovich", "accountId": "0"},
                   "self": "random.url/one", "created": "2021-12-31 10:00:00",
                   "updated": "2021-12-31 10:00:00", "started": "2021-12-31 09:00:00",
                   "timeSpentSeconds": 3600, "timeSpent": "1h", "id": '02', "issueId": '02'}))
        WorklogWithInfo(json_data=self.worklog_data_for_filters_test_1).save()
        self.worklog_data_for_filters_test_2 = loads(
            dumps({"author": {"displayName": "Test Testovich", "accountId": "1"},
                   "self": "random.url/two", "created": "2022-01-01 10:00:00",
                   "updated": "2022-01-01 10:00:00", "started": "2022-01-01 09:00:00",
                   "timeSpentSeconds": 3600, "timeSpent": "1h", "id": "03", "issueId": "03"}))
        WorklogWithInfo(json_data=self.worklog_data_for_filters_test_2).save()

        # 2.3. Model fields
        self.test_data_worklog_fields = ['id', 'url', 'display_name', 'account_id', 'created', 'updated', 'started',
                                         'time_spent_seconds', 'time_spent', 'jira_id', 'issueId', 'issue']

        # 3. GROUPED WORKLOGS DATA

        # 3.1. URLs
        self.grouped_by_projects_worklogs_view = 'https://jira-wl.wbtech.pro/jira-client-api/grouped-worklogs/'
        self.grouped_by_issues_worklogs_view = 'https://jira-wl.wbtech.pro/jira-client-api/grouped-by-issues-worklogs/'

        # 3.2. Model instances
        FinologOrder.save_from_jira_finolog_tuples([('TEST-234', 3)])

        # 4. FINOLOG PROJECTS DATA

        # 4.1. URLs
        self.finolog_projects_view = 'http://jira-wl.lvh.me/jira-client-api/finolog-projects/'

        # 4.2. Model instances
        FinologProject(**{'jira_key': 'add_test', 'finolog_id': '3'}).save()
        self.finolog_project_data_for_creation = {'jira_key': 'creation_test', 'finolog_id': '1'}

        return super().setUp()

    def tearDown(self):
        return super().tearDown()
