# Generated by Django 3.2.3 on 2021-05-21 00:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('predictions', '0003_auto_20210521_0041'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='userpredictions',
            name='summary',
        ),
        migrations.AddField(
            model_name='predictionpoints',
            name='note',
            field=models.TextField(default='Дал си прогноза за мача: 1 т.'),
        ),
    ]