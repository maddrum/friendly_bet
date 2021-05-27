# Generated by Django 3.2.3 on 2021-05-27 21:23

from django.conf import settings
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('matches', '0003_matchresult_match_is_over'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('predictions', '0004_auto_20210521_0043'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='userpredictions',
            unique_together={('user', 'match')},
        ),
    ]