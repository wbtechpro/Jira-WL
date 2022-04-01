from django.db.models import Sum

from .test_views_and_serializers_setup import ViewsAndSerializersTestSetUp
from client.models import WorklogWithInfo


class GroupedByProjectWorklogsViewAndSerializer(ViewsAndSerializersTestSetUp):

    def test_grouped_by_projects_view_and_serializer_get(self):
        """
        Проверяет работу вью и сериализатора, которые возвращают информацию о конкретных проектах, заказах и
        затраченном на них времени, а также общее затраченное на все проекты и заказы время, с методом get
        Сериализатор также добавляет ключ проекта (jira_key) в том случае, если заказ был согласован
        """
        response = self.client.get(self.grouped_by_projects_worklogs_view)

        self.assertEqual(response.status_code, 200)
        # Проверка отображения информации о затраченном на все проекты и заказы времени (def _get_ret_dict)
        self.assertEqual(response.data['all_logged_seconds'], WorklogWithInfo.objects.aggregate(
            Sum('time_spent_seconds'))['time_spent_seconds__sum'])
        self.assertEqual(len(response.data['grouped_worklogs']), 3)

        # Проверка ворклога, у которого не указан проект и на который отсутствует заказ в Финологе (данные только в
        # БД WorklogWithInfo)
        self.assertEqual(response.data['grouped_worklogs'][0]['issue__project'], None)
        self.assertEqual(response.data['grouped_worklogs'][0]['logged_time'], 3600)
        self.assertEqual(response.data['grouped_worklogs'][0]['issue__agreed_order_finolog__finolog_id'], None)
        self.assertEqual(response.data['grouped_worklogs'][0]['issue__agreed_order_finolog__jira_key'], "")
        self.assertEqual(response.data['grouped_worklogs'][0]['issue__project_finolog_id'], 0)

        # Проверка ворклога, у которого указан проект и заказ в Финологе (данные в БД WorklogWithInfo, IssuesInfo,
        # FinologOrder, FinologProject)
        self.assertEqual(response.data['grouped_worklogs'][1]['issue__project'], 'add_test')
        self.assertEqual(response.data['grouped_worklogs'][1]['logged_time'], 3600)
        self.assertEqual(response.data['grouped_worklogs'][1]['issue__agreed_order_finolog__finolog_id'], '3')
        self.assertEqual(response.data['grouped_worklogs'][1]['issue__agreed_order_finolog__jira_key'], 'TEST-234')
        self.assertEqual(response.data['grouped_worklogs'][1]['issue__project_finolog_id'], 3)

        # Проверка ворклога, у которого указан проект, однако в Финологе отсутствует информация о заказе (данные в БД
        # WorklogWithInfo, IssuesInfo)
        self.assertEqual(response.data['grouped_worklogs'][2]['issue__project'], 'test')
        self.assertEqual(response.data['grouped_worklogs'][2]['logged_time'], 3600)
        self.assertEqual(response.data['grouped_worklogs'][2]['issue__agreed_order_finolog__finolog_id'], None)
        self.assertEqual(response.data['grouped_worklogs'][2]['issue__agreed_order_finolog__jira_key'], "")
        self.assertEqual(response.data['grouped_worklogs'][2]['issue__project_finolog_id'], 0)

    def test_grouped_by_projects_view_and_serializer_head(self):
        """
        Проверяет работу вью и сериализатора, которые возвращают информацию о конкретных проектах, заказах и
        затраченном на них времени, а также общее затраченное на все проекты и заказы время, с методом head
        """
        response = self.client.head(self.grouped_by_projects_worklogs_view)
        self.assertEqual(response.status_code, 200)
        # Проверка отображения информации о затраченном на все проекты и заказы времени (def _get_ret_dict)
        self.assertEqual(response.data['all_logged_seconds'], WorklogWithInfo.objects.aggregate(
        Sum('time_spent_seconds'))['time_spent_seconds__sum'])
        self.assertEqual(len(response.data['grouped_worklogs']), 3)

        # Проверка ворклога, у которого не указан проект и на который отсутствует заказ в Финологе (данные только в
        # БД WorklogWithInfo)
        self.assertEqual(response.data['grouped_worklogs'][0]['issue__project'], None)
        self.assertEqual(response.data['grouped_worklogs'][0]['logged_time'], 3600)
        self.assertEqual(response.data['grouped_worklogs'][0]['issue__agreed_order_finolog__finolog_id'], None)
        self.assertEqual(response.data['grouped_worklogs'][0]['issue__agreed_order_finolog__jira_key'], "")
        self.assertEqual(response.data['grouped_worklogs'][0]['issue__project_finolog_id'], 0)

        # Проверка ворклога, у которого указан проект и заказ в Финологе (данные в БД WorklogWithInfo, IssuesInfo,
        # FinologOrder, FinologProject)
        self.assertEqual(response.data['grouped_worklogs'][1]['issue__project'], 'add_test')
        self.assertEqual(response.data['grouped_worklogs'][1]['logged_time'], 3600)
        self.assertEqual(response.data['grouped_worklogs'][1]['issue__agreed_order_finolog__finolog_id'], '3')
        self.assertEqual(response.data['grouped_worklogs'][1]['issue__agreed_order_finolog__jira_key'], 'TEST-234')
        self.assertEqual(response.data['grouped_worklogs'][1]['issue__project_finolog_id'], 3)

        # Проверка ворклога, у которого указан проект, однако в Финологе отсутствует информация о заказе (данные в БД
        # WorklogWithInfo, IssuesInfo)
        self.assertEqual(response.data['grouped_worklogs'][2]['issue__project'], 'test')
        self.assertEqual(response.data['grouped_worklogs'][2]['logged_time'], 3600)
        self.assertEqual(response.data['grouped_worklogs'][2]['issue__agreed_order_finolog__finolog_id'], None)
        self.assertEqual(response.data['grouped_worklogs'][2]['issue__agreed_order_finolog__jira_key'], "")
        self.assertEqual(response.data['grouped_worklogs'][2]['issue__project_finolog_id'], 0)

    def test_grouped_by_projects_view_and_serializer_prohibited_methods(self):
        """
        Проверяет, что вью не работает с http-методами, помимо указанных (get, head)
        """
        response = self.client.post(self.grouped_by_projects_worklogs_view)
        self.assertEqual(response.status_code, 405)

    # КОММЕНТАРИЙ ОТНОСИТЕЛЬНО ПАГИНАЦИИ СГРУППИРОВАННЫХ ПО ПРОЕКТАМ ВОРКЛОГОВ

    # Несмотря на то, что в коде (views.grouped.py, class GroupedByProjectWorklogView, func. list) предусмотрена
    # пагинация, в проекте не установлен размер страницы. Согласно документации, в таких случаях настройки считаются
    # установленными на None ("Both DEFAULT_PAGINATION_CLASS and PAGE_SIZE are None by default"), а значит,
    # пагинация в проекте не работает ("Pagination can be turned off by setting the pagination class to None").
    # Соответственно, эта часть кода не покрыта тестами


class GroupedByIssuesWorklogsViewAndSerializer(ViewsAndSerializersTestSetUp):

    def test_grouped_by_issues_view_and_serializer_get(self):
        """
        Проверяет работу вью и сериализатора, которые возвращают информацию о конкретных тасках, заказах и
        затраченном на них времени, а также общее затраченное на все таски и заказы время, с методом get
        """
        response = self.client.get(self.grouped_by_issues_worklogs_view)
        self.assertEqual(response.status_code, 200)

        # Проверка отображения информации о затраченном на все таски и заказы времени (def _get_ret_dict)
        self.assertEqual(response.data['all_logged_seconds'], WorklogWithInfo.objects.aggregate(
            Sum('time_spent_seconds'))['time_spent_seconds__sum'])
        self.assertEqual(len(response.data['grouped_worklogs']), 3)

        # Проверка ворклога, у которого не указан таск и на который отсутствует заказ в Финологе (данные только в
        # БД WorklogWithInfo)
        self.assertEqual(response.data['grouped_worklogs'][0]['logged_time'], 3600)
        self.assertEqual(response.data['grouped_worklogs'][0]['issue__agreed_order_finolog__finolog_id'], None)
        self.assertEqual(response.data['grouped_worklogs'][0]['issue__key'], None)

        # Проверка ворклога, у которого указан таск и заказ в Финологе (данные в БД WorklogWithInfo, IssuesInfo,
        # FinologOrder)
        self.assertEqual(response.data['grouped_worklogs'][1]['logged_time'], 3600)
        self.assertEqual(response.data['grouped_worklogs'][1]['issue__agreed_order_finolog__finolog_id'], '3')
        self.assertEqual(response.data['grouped_worklogs'][1]['issue__key'], 'add_test-234')

        # Проверка ворклога, у которого указан таск, однако в Финологе отсутствует информация о заказе (данные в БД
        # WorklogWithInfo, IssuesInfo)
        self.assertEqual(response.data['grouped_worklogs'][2]['logged_time'], 3600)
        self.assertEqual(response.data['grouped_worklogs'][2]['issue__agreed_order_finolog__finolog_id'], None)
        self.assertEqual(response.data['grouped_worklogs'][2]['issue__key'], 'test-123')

    def test_grouped_by_issues_view_and_serializer_head(self):
        """
        Проверяет работу вью и сериализатора, которые возвращают информацию о конкретных проектах, заказах и
        затраченном на них времени, а также общее затраченное на все проекты и заказы время, с методом head
        """
        response = self.client.head(self.grouped_by_issues_worklogs_view)
        self.assertEqual(response.status_code, 200)

        # Проверка отображения информации о затраченном на все таски и заказы времени (def _get_ret_dict)
        self.assertEqual(response.data['all_logged_seconds'], WorklogWithInfo.objects.aggregate(
            Sum('time_spent_seconds'))['time_spent_seconds__sum'])
        self.assertEqual(len(response.data['grouped_worklogs']), 3)

        # Проверка ворклога, у которого не указан таск и на который отсутствует заказ в Финологе (данные только в
        # БД WorklogWithInfo)
        self.assertEqual(response.data['grouped_worklogs'][0]['logged_time'], 3600)
        self.assertEqual(response.data['grouped_worklogs'][0]['issue__agreed_order_finolog__finolog_id'],
                         None)
        self.assertEqual(response.data['grouped_worklogs'][0]['issue__key'], None)

        # Проверка ворклога, у которого указан таск и заказ в Финологе (данные в БД WorklogWithInfo, IssuesInfo,
        # FinologOrder)
        self.assertEqual(response.data['grouped_worklogs'][1]['logged_time'], 3600)
        self.assertEqual(response.data['grouped_worklogs'][1]['issue__agreed_order_finolog__finolog_id'], '3')
        self.assertEqual(response.data['grouped_worklogs'][1]['issue__key'], 'add_test-234')

        # Проверка ворклога, у которого указан таск, однако в Финологе отсутствует информация о заказе (данные в БД
        # WorklogWithInfo, IssuesInfo)
        self.assertEqual(response.data['grouped_worklogs'][2]['logged_time'], 3600)
        self.assertEqual(response.data['grouped_worklogs'][2]['issue__agreed_order_finolog__finolog_id'],
                         None)
        self.assertEqual(response.data['grouped_worklogs'][2]['issue__key'], 'test-123')

    def test_grouped_by_issues_view_and_serializer_prohibited_methods(self):
        """
        Проверяет, что вью не работает с http-методами, помимо указанных (get, head)
        """
        response = self.client.post(self.grouped_by_issues_worklogs_view)
        self.assertEqual(response.status_code, 405)
