# Generated by Django 3.2 on 2022-03-07 13:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('client', '0004_auto_20220221_0810'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='daysfordownloadmodel',
            options={'verbose_name_plural': '! Количество дней, за которые необходимо загрузить ворклоги'},
        ),
        migrations.AlterField(
            model_name='finologproject',
            name='finolog_id',
            field=models.CharField(max_length=50, unique=True),
        ),
        migrations.AlterField(
            model_name='finologproject',
            name='jira_key',
            field=models.CharField(max_length=50, unique=True),
        ),
    ]