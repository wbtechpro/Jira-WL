from rest_framework import serializers

from client.models import WorklogWithInfo, IssuesInfo


class WorklogSerializer(serializers.ModelSerializer):
    class Meta:
        model = WorklogWithInfo
        exclude = ('json_data',)


class IssueSerializer(serializers.ModelSerializer):
    class Meta:
        model = IssuesInfo
        exclude = ('json_data',)
