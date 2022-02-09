from json import dumps, loads

from client.models.issue import *
from .test_models_setup import IssuesInfoTestsSetUp


class IssueModelTest(IssuesInfoTestsSetUp):

    def test_issue_queryset_returns_unique_agreed_order_key(self):
        """
        Проверяет, действительно ли менеджер IssueQuerySet возвращает данные модели IssuesInfo с уникальным значением
        agreed_order_key.
        Для теста в БД IssuesInfo добавлены два таска с несогласованными заказами ("not_agreed_order")
        """
        model_data = IssuesInfo.objects.values('agreed_order_key')
        model_data_unique_orders = model_data.distinct('agreed_order_key')
        test_instances = IssuesInfo.objects.unique_agreed_keys()
        self.assertEqual(len(model_data), 2)
        self.assertEqual(len(model_data_unique_orders), 1)
        self.assertQuerysetEqual(model_data_unique_orders, test_instances)

    def test_string_issue_name_representation(self):
        """
        Проверяет работу метода __str__, который должен возвращать название таска
        """
        model_data = IssuesInfo.objects.all().first()
        self.assertEqual(model_data.__str__(), 'random0')

    def test_save_data_from_json(self):
        """
        Проверяет работу переопределенного метода save, который берет данные для модели из JSON, полученного из Jira API
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
        Проверяет работу метода-свойства is_agreed_order, который проверят, есть ли у заказа специальное поле
        отправки в Финолог
        """
        IssuesInfo(json_data=self.instance_data_2).save()
        instance_data_1 = IssuesInfo.objects.all().last().is_agreed_order
        instance_data_2 = IssuesInfo.objects.all().first().is_agreed_order
        self.assertTrue(instance_data_1)
        self.assertFalse(instance_data_2)

    def test_get_agreed_order_key(self):
        """
        Проверяет работу метода _get_agreed_order_key, который заполняет поле индекса заказа в зависимости от того,
        согласован ли он, и, если да, то является ли таск сам согласованным заказом или имеет родительский заказ
        """
        instance_data_0 = IssuesInfo.objects.all().first()._get_agreed_order_key()  # таск с несогласованным заказом
        IssuesInfo(json_data=self.instance_data_2).save()
        instance_data_1 = IssuesInfo.objects.all().last()._get_agreed_order_key()  # таск, сам являющийся заказом
        IssuesInfo(json_data=self.instance_data_3).save()
        instance_data_2 = IssuesInfo.objects.all().last()._get_agreed_order_key()  # таск, имеющий родительский заказ
        self.assertEqual(instance_data_0, 'not_agreed_order')
        self.assertEqual(instance_data_1, 'test-123')
        self.assertEqual(instance_data_2, 'TEST-123')
