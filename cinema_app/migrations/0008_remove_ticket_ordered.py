# Generated by Django 4.2.4 on 2023-08-19 12:09

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('cinema_app', '0007_alter_ticket_date_of_order'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='ticket',
            name='ordered',
        ),
    ]
