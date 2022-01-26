from json import dumps, loads

from rest_framework.test import APITestCase

from client.models import IssuesInfo


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
