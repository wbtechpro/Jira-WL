# Generated by Django 3.2 on 2022-03-30 10:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('client', '0010_rename_start_date_periodfordownloadmodel_end_date'),
    ]

    operations = [
        migrations.AlterField(
            model_name='finologproject',
            name='category_id',
            field=models.CharField(blank=True, max_length=250, null=True),
        ),
    ]