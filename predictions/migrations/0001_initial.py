# Generated by Django 3.2.3 on 2021-05-16 17:23

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('events', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('matches', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='UserScores',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('points', models.IntegerField(default=0, null=True)),
                ('bonus_points_added', models.BooleanField(default=False)),
                ('event', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='event_points', to='events.event')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='user_points', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='UserPredictions',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('goals_home', models.IntegerField(default=0)),
                ('goals_guest', models.IntegerField(default=0)),
                ('summary', models.TextField(default='Дал си прогноза за мача: 1 т.')),
                ('created_on', models.DateTimeField(auto_now_add=True)),
                ('edited_on', models.DateTimeField(auto_now=True)),
                ('match', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='match', to='matches.matches')),
                ('match_state', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='events.eventmatchstates')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='predictions', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='UserMatchPoints',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('points_gained', models.IntegerField(default=0)),
                ('created_on', models.DateTimeField(auto_now_add=True)),
                ('edited_on', models.DateTimeField(auto_now=True)),
                ('match', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='matches.matches')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='user_match_points', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
