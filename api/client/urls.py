from django.urls import path
from rest_framework.routers import DefaultRouter

from client.views import BaseIssueListView, BaseWorklogListView, GroupedByProjectWorklogView, FinologProjectViewSet


router = DefaultRouter()
router.register(r'finolog-projects', FinologProjectViewSet, basename='finolog-project')
urlpatterns = router.urls


urlpatterns += [
    path('issues/', BaseIssueListView.as_view()),
    path('worklogs/', BaseWorklogListView.as_view()),
    path('grouped-worklogs/', GroupedByProjectWorklogView.as_view()),
]
