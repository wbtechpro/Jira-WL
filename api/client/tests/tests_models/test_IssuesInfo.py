from json import dumps, loads

from client.models.issue import *
from .test_models_setup import IssuesInfoTestsSetUp


class IssueModelTest(IssuesInfoTestsSetUp):

    def test_issue_queryset_returns_unique_agreed_order_key(self):
        """
        Checks if the IssueQuerySet manager actually returns data from the IssuesInfo model with a unique
        agreed_order_key value. For the test, two tasks with non-agreed orders ("not_agreed_order") have been added
        to the IssuesInfo database
        """
        model_data = IssuesInfo.objects.values('agreed_order_key')
        model_data_unique_orders = model_data.distinct('agreed_order_key')
        test_instances = IssuesInfo.objects.unique_agreed_keys()
        self.assertEqual(len(model_data), 2)
        self.assertEqual(len(model_data_unique_orders), 1)
        self.assertQuerysetEqual(model_data_unique_orders, test_instances)

    def test_string_issue_name_representation(self):
        """
        Checks the operation of the __str__ method, which should return the name of the task
        """
        model_data = IssuesInfo.objects.all().first()
        self.assertEqual(model_data.__str__(), 'random0')

    def test_save_data_from_json(self):
        """
        Tests the work of the overridden save method, which takes data for the model from JSON received from the Jira
        API
        """
        instance_json_data = loads(dumps({"self": "random.url/test", "fields": {"summary": "test"},
                                          "key": "test-123", "id": 1, "agreed_order_key": "not_agreed_order"}))
        IssuesInfo(json_data=instance_json_data).save()
        instance_data = IssuesInfo.objects.all().last()
        self.assertEqual(instance_data.json_data, instance_json_data)
        self.assertEqual(instance_data.url, "random.url/test")
        self.assertEqual(instance_data.summary, "test")
        self.assertEqual(instance_data.project, "test")
        self.assertEqual(instance_data.key, "test-123")
        self.assertEqual(instance_data.jira_id, 1)
        self.assertEqual(instance_data.agreed_order_key, "not_agreed_order")

    def test_is_order_agreed(self):
        """
        Checks the operation of the is_agreed_order property method, which will check if the order has a special send
        field to Finolog
        """
        IssuesInfo(json_data=self.instance_data_2).save()
        instance_data_1 = IssuesInfo.objects.all().last().is_agreed_order
        instance_data_2 = IssuesInfo.objects.all().first().is_agreed_order
        self.assertTrue(instance_data_1)
        self.assertFalse(instance_data_2)

    def test_get_agreed_order_key(self):
        """
        Checks the operation of the _get_agreed_order_key method, which populates the order index field depending on
        whether it is matched, and, if so, whether the task itself is a matched order or has a parent order
        """
        instance_data_0 = IssuesInfo.objects.all().first()._get_agreed_order_key()  # task with a non-agreed order
        IssuesInfo(json_data=self.instance_data_2).save()
        instance_data_1 = IssuesInfo.objects.all().last()._get_agreed_order_key()  # a task that is itself an order
        IssuesInfo(json_data=self.instance_data_3).save()
        instance_data_2 = IssuesInfo.objects.all().last()._get_agreed_order_key()  # a task that has a parent order
        self.assertEqual(instance_data_0, 'not_agreed_order')
        self.assertEqual(instance_data_1, 'test-123')
        self.assertEqual(instance_data_2, 'TEST-123')
