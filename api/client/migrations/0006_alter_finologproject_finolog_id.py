# Generated by Django 3.2 on 2022-03-07 13:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('client', '0005_auto_20220307_1328'),
    ]

    operations = [
        migrations.AlterField(
            model_name='finologproject',
            name='finolog_id',
            field=models.CharField(max_length=50),
        ),
    ]
