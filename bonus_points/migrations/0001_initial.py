# Generated by Django 3.2.3 on 2021-05-22 13:19

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('events', '0012_eventphases_multiplier'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='BonusDescription',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200)),
                ('active_until', models.DateTimeField()),
                ('correct_answer', models.CharField(blank=True, max_length=500, null=True)),
                ('points', models.IntegerField()),
                ('available_choices', models.CharField(blank=True, max_length=600, null=True)),
                ('bonus_input', models.CharField(choices=[('text', 'text'), ('number', 'number'), ('all-countries', 'all-countries'), ('choices', 'choices')], default='text', max_length=20)),
                ('auto_bonus', models.BooleanField(default=False, help_text='If this is checked, all users will be included to participate in this bonus by default.')),
                ('bonus_active', models.BooleanField(default=False)),
                ('created_on', models.DateTimeField(auto_now_add=True)),
                ('edited_on', models.DateTimeField(auto_now=True)),
                ('event', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='event', to='events.event')),
            ],
        ),
        migrations.CreateModel(
            name='BonusUserPrediction',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('user_prediction', models.CharField(max_length=500)),
                ('created_on', models.DateTimeField(auto_now_add=True)),
                ('edited_on', models.DateTimeField(auto_now=True)),
                ('bonus', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='bonus', to='bonus_points.bonusdescription')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='bonus_user', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='UserBonusSummary',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('total_bonus_points', models.IntegerField()),
                ('total_summary', models.TextField()),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='user', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='BonusUserScore',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('points_gained', models.IntegerField(default=0)),
                ('summary_text', models.CharField(max_length=500)),
                ('created_on', models.DateTimeField(auto_now_add=True)),
                ('edited_on', models.DateTimeField(auto_now=True)),
                ('prediction', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='prediction', to='bonus_points.bonususerprediction')),
            ],
        ),
    ]
