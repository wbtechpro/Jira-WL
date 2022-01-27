from json import dumps, loads

from rest_framework.test import APITestCase

from client.models import IssuesInfo, FinologOrder, FinologProject, WorklogWithInfo


class IssuesInfoTestsSetUp(APITestCase):
    def setUp(self):
        self.instance_data_0 = loads(dumps({"self": "random.url/zero", "fields": {"summary": "random0"},
                                            "key": "random0", "id": 0, "agreed_order_key": "not_agreed_order"}))
        IssuesInfo(json_data=self.instance_data_0).save()
        self.instance_data_1 = loads(dumps({"self": "random.url/one", "fields": {"summary": "random1"},
                                            "key": "random1", "id": 1, "agreed_order_key": "mot_agreed_order"}))
        IssuesInfo(json_data=self.instance_data_1).save()
        self.instance_data_2 = loads(dumps({"self": "random.url/test",
                                            "fields": {"summary": "test",
                                                       "customfield_10376": [{"value": "Отправить"}]},
                                            "key": "test-123", "id": 1}))
        self.instance_data_3 = loads(dumps({"self": "random.url/test",
                                            "fields": {"summary": "test", "customfield_10100": 'TEST-123'},
                                            "key": "test-123", "id": 1}))

        return super().setUp()

    def tearDown(self):
        return super().tearDown()


class FinologModelsTestsSetUp(APITestCase):
    def setUp(self):
        self.instance_data_0 = {'jira_key': 'RAND000', 'finolog_id': 0}
        FinologOrder(**self.instance_data_0).save()
        self.jira_finolog_tuples = [('RAND001', 1)]
        self.instance_data_1 = loads(dumps({"self": "random.url/rand", "fields": {"summary": "random0",
                                            "customfield_10376": [{"value": "Отправить"}]},
                                            "key": "RAND001", "id": 1}))
        IssuesInfo(json_data=self.instance_data_1).save()
        self.instance_data_2 = {'jira_key': 'RAND', 'finolog_id': 222}
        FinologProject(**self.instance_data_2).save()

        return super().setUp()

    def tearDown(self):
        return super().tearDown()


class WorklogWithInfoTestsSetUp(APITestCase):
    def setUp(self):
        self.instance_data_0 = loads(dumps({"author": {"displayName": "Random Randomovich", "accountId": "0"},
                                            "self": "random.url/zero", "created": "2022-01-01 10:00:00",
                                            "updated": "2022-01-01 10:00:00", "started": "2022-01-01 09:00:00",
                                            "timeSpentSeconds": 3600, "timeSpent": "1h", "id": '00', "issueId": '00'}))
        WorklogWithInfo(json_data=self.instance_data_0).save()
        self.instance_data_1 = loads(dumps({"author": {"displayName": "Test Testovich", "accountId": "1"},
                                            "self": "random.url/one", "created": "2022-01-01 10:00:00",
                                            "updated": "2022-01-01 10:00:00", "started": "2022-01-01 09:00:00",
                                            "timeSpentSeconds": 3600, "timeSpent": "1h", "id": "01", "issueId": "01"}))
        WorklogWithInfo(json_data=self.instance_data_1).save()
        self.instance_data_2 = loads(dumps({"author": {"displayName": "Test Testovich", "accountId": "1"},
                                            "self": "random.url/one", "created": "2022-01-01 10:00:00",
                                            "updated": "2022-01-01 10:00:00", "started": "2022-01-01 09:00:00",
                                            "timeSpentSeconds": 3600, "timeSpent": "1h", "id": "02", "issueId": "02"}))
        WorklogWithInfo(json_data=self.instance_data_2).save()
        # self.instance_data_1 = loads(dumps({"self": "random.url/one", "fields": {"summary": "random1"},
        #                                     "key": "random1", "id": 1, "agreed_order_key": "mot_agreed_order"}))
        # IssuesInfo(json_data=self.instance_data_1).save()
        # self.instance_data_2 = loads(dumps({"self": "random.url/test",
        #                                     "fields": {"summary": "test",
        #                                                "customfield_10376": [{"value": "Отправить"}]},
        #                                     "key": "test-123", "id": 1}))
        # self.instance_data_3 = loads(dumps({"self": "random.url/test",
        #                                     "fields": {"summary": "test", "customfield_10100": 'TEST-123'},
        #                                     "key": "test-123", "id": 1}))

        return super().setUp()

    def tearDown(self):
        return super().tearDown()