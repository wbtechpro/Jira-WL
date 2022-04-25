from rest_framework import serializers
from django.shortcuts import get_object_or_404
from rest_framework import viewsets
from rest_framework.response import Response

from client.models import FinologProject


class FinologProjectSerializer(serializers.ModelSerializer):

    class Meta:
        model = FinologProject
        fields = '__all__'


class FinologProjectViewSet(viewsets.ViewSet):

    def list(self, request):
        queryset = FinologProject.objects.all()
        serializer = FinologProjectSerializer(queryset, many=True)
        return Response(serializer.data)

    def retrieve(self, request, pk=None):
        queryset = FinologProject.objects.all()
        finolog_project = get_object_or_404(queryset, pk=pk)
        serializer = FinologProjectSerializer(finolog_project)
        return Response(serializer.data)

    def create(self, request):
        serializer = FinologProjectSerializer(data=request.data)
        serializer.is_valid()
        serializer.save()
        return Response(serializer.data, status=201)

    def update(self, request, pk=None):
        data = request.data
        queryset = FinologProject.objects.all()
        finolog_project = get_object_or_404(queryset, pk=pk)
        finolog_project.jira_key = data['jira_key']
        finolog_project.finolog_id = data['finolog_id']
        if 'category_id' in data.keys():
            finolog_project.cateory_id = data['category_id']
        serializer = FinologProjectSerializer(finolog_project)
        return Response(serializer.data, status=200)
