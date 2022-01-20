# Generated by Django 3.2 on 2021-04-16 11:14

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='FinologApiToken',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('token', models.CharField(max_length=150, verbose_name='токен')),
            ],
            options={
                'verbose_name': 'Токен Финолога',
                'verbose_name_plural': 'Токены Финолога',
            },
        ),
        migrations.CreateModel(
            name='FinologOrder',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('jira_key', models.CharField(max_length=50)),
                ('finolog_id', models.CharField(max_length=50)),
            ],
        ),
        migrations.CreateModel(
            name='IssuesInfo',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('json_data', models.JSONField()),
                ('url', models.URLField(verbose_name='ссылка на таск')),
                ('summary', models.TextField(verbose_name='summary')),
                ('project', models.CharField(max_length=50, verbose_name='project')),
                ('key', models.CharField(max_length=50, verbose_name='key')),
                ('jira_id', models.IntegerField(verbose_name='issue jira id')),
                ('agreed_order_key', models.CharField(blank=True, max_length=50, null=True, verbose_name='Ключ заказа (если относится к заказу)')),
                ('agreed_order_finolog', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='client.finologorder')),
            ],
        ),
        migrations.CreateModel(
            name='WorklogWithInfo',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('json_data', models.JSONField()),
                ('url', models.URLField(verbose_name='ссылка на ворклог')),
                ('display_name', models.CharField(max_length=50, verbose_name='displayName')),
                ('account_id', models.CharField(max_length=50, verbose_name='accountId')),
                ('created', models.DateTimeField(verbose_name='created')),
                ('updated', models.DateTimeField(verbose_name='updated')),
                ('started', models.DateTimeField(verbose_name='started')),
                ('time_spent_seconds', models.IntegerField(verbose_name='timeSpentSeconds')),
                ('time_spent', models.CharField(max_length=50, verbose_name='timeSpent')),
                ('jira_id', models.CharField(max_length=50, verbose_name='worklog jira id')),
                ('issueId', models.CharField(max_length=50, verbose_name='issueId')),
                ('issue', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='worklogs', to='client.issuesinfo', verbose_name='Таск, связанный по issueId')),
            ],
            options={
                'verbose_name': 'Ворклог',
                'verbose_name_plural': 'Ворклоги',
                'ordering': ('updated',),
            },
        ),
    ]