# Generated by Django 5.0 on 2025-06-24 12:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('private_module', '0004_privatemessage_created_at'),
    ]

    operations = [
        migrations.AddField(
            model_name='privatemessage',
            name='is_read',
            field=models.BooleanField(default=False),
        ),
    ]
