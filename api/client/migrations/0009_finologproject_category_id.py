# Generated by Django 3.2 on 2022-03-21 14:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('client', '0008_alter_periodfordownloadmodel_options'),
    ]

    operations = [
        migrations.AddField(
            model_name='finologproject',
            name='category_id',
            field=models.CharField(max_length=250, null=True),
        ),
    ]
