# Generated by Django 3.0.6 on 2020-05-29 19:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0011_alert_trigger_value'),
    ]

    operations = [
        migrations.AddField(
            model_name='alert',
            name='is_notified',
            field=models.BooleanField(default=False),
        ),
    ]