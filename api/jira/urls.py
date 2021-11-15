from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
    path('jira-client-admin/', admin.site.urls),
    path('jira-client-api-auth/', include('rest_framework.urls')),
    path('jira-client-api/', include('client.urls')),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

urlpatterns += [
    path('sentry-debug', lambda request: 1 / 0),  # trigger error to check sentry
]