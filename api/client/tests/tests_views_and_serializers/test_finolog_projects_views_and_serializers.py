from collections import OrderedDict

from .test_views_and_serializers_setup import ViewsAndSerializersTestSetUp
from client.models import FinologProject


class GroupedByProjectWorklogsViewAndSerializer(ViewsAndSerializersTestSetUp):

    def test_finolog_projects_view_and_serializer_display_get(self):
        """
        Проверяет работу функции list вью и сериализатора, которые отображают данные о проектах, согласованных
        как заказ в Финологе, из БД FinologProject, с методом get
        Для тестов в БД додавлен один проект
        """
        response = self.client.get(self.finolog_projects_view)
        finolog_projects__info = FinologProject.objects.values()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), len(finolog_projects__info))
        self.assertEqual(response.data[0], OrderedDict(list((x, y) for x, y in finolog_projects__info[0].items())))

    def test_finolog_projects_view_and_serializer_display_head(self):
        """
        Проверяет работу функции list вью и сериализатора, которые отображают данные о проектах, согласованных
        как заказ в Финологе, из БД FinologProject, с методом head
        """
        response = self.client.head(self.finolog_projects_view)
        finolog_projects__info = FinologProject.objects.values()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), len(finolog_projects__info))
        self.assertEqual(response.data[0], OrderedDict(list((x, y) for x, y in finolog_projects__info[0].items())))

    def test_finolog_projects_view_and_serializer_retrieve_get_with_existent_pk(self):
        """
        Проверяет работу функции retrieve вью и сериализатора, которые отображают данные о проектах,
        согласованных как заказ в Финологе, из БД FinologProject, с методом get и с существующим pk
        """
        finolog_projects_info = FinologProject.objects.first()
        response = self.client.get(self.finolog_projects_view + f'{finolog_projects_info.pk}/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['id'], finolog_projects_info.pk)
        self.assertEqual(response.data['jira_key'], finolog_projects_info.jira_key)
        self.assertEqual(response.data['finolog_id'], finolog_projects_info.finolog_id)

    def test_finolog_projects_view_and_serializer_retrieve_get_with_nonexistent_pk(self):
        """
        Проверяет работу функции retrieve вью и сериализатора, которые отображают данные о проектах,
        согласованных как заказ в Финологе, из БД FinologProject, с методом get и с существующим pk
        """
        response = self.client.get(self.finolog_projects_view + '11111111/')
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.data, {"detail": "Not found."})

    def test_finolog_projects_view_and_serializer_retrieve_head_with_existent_pk(self):
        """
        Проверяет работу функции retrieve вью и сериализатора, которые отображают данные о проектах,
        согласованных как заказ в Финологе, из БД FinologProject, с методом head и с существующим pk
        """
        finolog_projects_info = FinologProject.objects.first()
        response = self.client.head(self.finolog_projects_view + f'{finolog_projects_info.pk}/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['id'], finolog_projects_info.pk)
        self.assertEqual(response.data['jira_key'], finolog_projects_info.jira_key)
        self.assertEqual(response.data['finolog_id'], finolog_projects_info.finolog_id)

    def test_finolog_projects_view_and_serializer_retrieve_head_with_nonexistent_pk(self):
        """
        Проверяет работу функции retrieve вью и сериализатора, которые отображают данные о проектах,
        согласованных как заказ в Финологе, из БД FinologProject, с методом head и с существующим pk
        """
        response = self.client.head(self.finolog_projects_view + '11111111/')
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.data, {"detail": "Not found."})

    def test_finolog_projects_view_and_serializer_creation(self):
        """
        Проверяет работу функции create вью, которая валидирует данные и в случае успеха создает новую запись в БД
        FinologProjects
        В текущий момент в БД FinologProject находится один проект. По итогу работы теста должен быть создан второй
        """
        response = self.client.post(self.finolog_projects_view, self.finolog_project_data_for_creation)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data, FinologProject.objects.values().last())
        response_2 = self.client.get(self.finolog_projects_view)
        self.assertEqual(len(response_2.data), len(FinologProject.objects.all()))

    def test_finolog_projects_view_and_serializer_creation_with_improper_methods(self):
        """
        Проверяет работу функции create вью, которая валидирует данные и в случае успеха создает новую запись в БД
        FinologProjects, с неправильным методом (get вместо post) В текущий момент в БД FinologProject находится один
        проект. По итогу работы создание второго не должно произойти - вместо этого должен отобразиться уже
        существующий проект
        """
        response = self.client.get(self.finolog_projects_view, self.finolog_project_data_for_creation)
        self.assertNotEqual(response.status_code, 201)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(len(FinologProject.objects.all()), 1)
        self.assertNotEqual(len(response.data), 2)
        self.assertNotEqual(len(FinologProject.objects.all()), 2)
        self.assertEqual(response.data[0], response.data[::-1][0])
        self.assertEqual(dict(response.data[0])['jira_key'], 'add_test')
        self.assertEqual(dict(response.data[0])['finolog_id'], '3')
        self.assertNotEqual(dict(response.data[0])['jira_key'], 'creation_test')
        self.assertNotEqual(dict(response.data[0])['finolog_id'], '1')
