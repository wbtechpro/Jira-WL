# Generated by Django 3.2 on 2022-02-21 08:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('client', '0003_proxymodel'),
    ]

    operations = [
        migrations.CreateModel(
            name='DaysForDownloadModel',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('days', models.IntegerField(blank=True, null=True)),
            ],
            options={
                'verbose_name': '! Количество дней, за которые необходимо загрузить ворклоги',
                'verbose_name_plural': '! Количество дней, за которые необходимо загрузить ворклоги',
            },
        ),
        migrations.DeleteModel(
            name='ProxyModel',
        ),
    ]
