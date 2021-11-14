from django.core.management.base import BaseCommand

from client.models import FinologProject


default_projects = (
    (118854, 'AREND'),
    (118959, 'BIOM'),
    (121411, 'BLOG'),
    (122467, 'DM'),
    (118857, 'HOB'),
    (118871, 'IN'),
    (125953, 'INFKB'),
    (118858, 'IZ'),
    (134145, 'JAMBA'),
    (124582, 'MPRO'),
    (127605, 'OTVET'),
    (162432, 'PLVD'),
    (137796, 'PRO'),
    (118877, 'SMMAS'),
    (118855, 'US'),
    (127607, 'VAL'),
    (134153, 'WBT'),
    (134153, 'REC'),
    (118856, 'Пивная на Парковой'),
)


class Command(BaseCommand):

    """
    (Пере)создает дефолтные проекты
    """

    help = 'Создает суперпользователя для админки'

    def handle(self, *args, **options):

        for finolog_id, jira_key in default_projects:
            FinologProject.objects.get_or_create(finolog_id=finolog_id, jira_key=jira_key)
        print('default projects (re)created')
