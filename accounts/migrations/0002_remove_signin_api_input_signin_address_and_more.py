# Generated by Django 4.1.5 on 2025-07-14 14:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='signin',
            name='api_input',
        ),
        migrations.AddField(
            model_name='signin',
            name='address',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='signin',
            name='phone_number',
            field=models.CharField(blank=True, max_length=20, null=True),
        ),
        migrations.AddField(
            model_name='signin',
            name='trading_account',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
    ]
