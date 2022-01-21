
from django_filters import rest_framework as filters
from rest_framework import generics

from client.models import WorklogWithInfo, IssuesInfo
from client.serializers import WorklogSerializer, IssueSerializer


class CharInFilter(filters.BaseInFilter, filters.CharFilter):  # фильтр на основе CVS для поиска нескольких тасков Жиры
    pass


class BaseWorklogWithInfoFilter(filters.FilterSet):
    updated_start_date = filters.DateTimeFilter(field_name="updated", lookup_expr='gte')
    updated_finish_date = filters.DateTimeFilter(field_name="updated", lookup_expr='lte')

    created_start_date = filters.DateTimeFilter(field_name="created", lookup_expr='gte')
    created_finish_date = filters.DateTimeFilter(field_name="created", lookup_expr='lte')

    started_start_date = filters.DateTimeFilter(field_name="started", lookup_expr='gte')
    started_finish_date = filters.DateTimeFilter(field_name="started", lookup_expr='lte')

    account_id = filters.CharFilter(field_name='account_id')

    issue__project = filters.CharFilter(field_name='issue__project')

    issue__key = CharInFilter(field_name='issue__key', lookup_expr='in')  # фильтрация по названиям тасков Жиры

    class Meta:
        model = WorklogWithInfo
        fields = ['updated', 'started', 'created', 'account_id', 'issue__project', 'issue__key']


class BaseWorklogListView(generics.ListAPIView):
    queryset = WorklogWithInfo.objects.all()
    serializer_class = WorklogSerializer
    http_method_names = ['get', 'head']
    filter_backends = [filters.DjangoFilterBackend]
    filterset_class = BaseWorklogWithInfoFilter


class BaseIssueListView(generics.ListAPIView):
    queryset = IssuesInfo.objects.all()
    serializer_class = IssueSerializer
    http_method_names = ['get', 'head']
    filter_backends = [filters.DjangoFilterBackend]
    filterset_fields = ['key', ]
