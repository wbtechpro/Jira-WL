# Generated by Django 3.2 on 2022-03-24 12:41

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('client', '0009_finologproject_category_id'),
    ]

    operations = [
        migrations.RenameField(
            model_name='periodfordownloadmodel',
            old_name='start_date',
            new_name='end_date',
        ),
    ]