# Generated by Django 3.2.3 on 2021-05-16 23:37

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('events', '0003_auto_20210516_2335'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='eventgroups',
            unique_together={('event', 'event_group')},
        ),
    ]
