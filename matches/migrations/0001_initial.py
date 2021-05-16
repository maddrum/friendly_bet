# Generated by Django 3.2.3 on 2021-05-16 17:23

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('events', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Matches',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('match_number', models.IntegerField()),
                ('match_start_time', models.DateTimeField()),
                ('created_on', models.DateTimeField(auto_now_add=True)),
                ('edited_on', models.DateTimeField(auto_now=True)),
                ('country_guest', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='country_guest', to='events.teams')),
                ('country_home', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='country_home', to='events.teams')),
                ('phase', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='match_phase', to='events.eventphases')),
            ],
            options={
                'unique_together': {('country_home', 'country_guest', 'phase')},
            },
        ),
        migrations.CreateModel(
            name='MatchResult',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('score_home', models.IntegerField(default=0)),
                ('score_guest', models.IntegerField(default=0)),
                ('score_after_penalties_home', models.IntegerField(default=0)),
                ('score_after_penalties_guest', models.IntegerField(default=0)),
                ('penalties', models.BooleanField(default=False)),
                ('created_on', models.DateTimeField(auto_now_add=True)),
                ('edited_on', models.DateTimeField(auto_now=True)),
                ('match', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='match_result', to='matches.matches')),
                ('match_state', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='events.eventmatchstates')),
            ],
        ),
    ]
