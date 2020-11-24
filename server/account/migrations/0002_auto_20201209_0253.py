# Generated by Django 3.1.3 on 2020-12-08 17:53

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='AccessLog',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('created_date', models.CharField(blank=True, max_length=10)),
                ('created_month', models.CharField(blank=True, max_length=7)),
                ('request_method', models.CharField(max_length=10)),
                ('requested_uri', models.URLField(blank=True)),
                ('query_string', models.CharField(blank=True, max_length=500)),
                ('status_code', models.IntegerField(null=True)),
                ('referer', models.URLField(blank=True)),
                ('user_agent', models.CharField(blank=True, max_length=500)),
                ('ip_addr', models.GenericIPAddressField(null=True)),
                ('latency', models.IntegerField(null=True)),
                ('comment', models.TextField(blank=True)),
                ('user', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'db_table': 'account_access_logs',
            },
        ),
        migrations.AddIndex(
            model_name='accesslog',
            index=models.Index(fields=['-created_month'], name='account_acc_created_47a863_idx'),
        ),
        migrations.AddIndex(
            model_name='accesslog',
            index=models.Index(fields=['-created_date'], name='account_acc_created_5a01ae_idx'),
        ),
    ]