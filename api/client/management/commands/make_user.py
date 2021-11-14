from django.core.management.base import BaseCommand

from django.contrib.auth import get_user_model


class Command(BaseCommand):

    """
    Создает суперпользователя
    """

    help = 'Создает суперпользователя для админки'

    def handle(self, *args, **options):

        User = get_user_model()
        User.objects.all().delete()
        User.objects.create_superuser('admin', 'admin@e.e', 'asDqAf1SSf4')
        print('superuser_recreated')
