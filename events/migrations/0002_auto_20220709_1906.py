# Generated by Django 3.2.3 on 2022-07-09 19:06

import django.core.validators
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('events', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='team',
            options={'ordering': ('-group__event_group', 'name')},
        ),
        migrations.CreateModel(
            name='PhaseBetPoint',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('points_state', models.SmallIntegerField(default=0, help_text='Defines how much points will be TAKEN from the user on FAILED bet on match state.', validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(1000)])),
                ('return_points_state', models.SmallIntegerField(default=0, help_text='Defines how much points will be GIVEN to the user on SUCCESS bet on match state.', validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(5000)])),
                ('points_result', models.SmallIntegerField(default=0, help_text='Defines how much points will be TAKEN from the user on FAILED bet on match result.', validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(1000)])),
                ('return_points_result', models.SmallIntegerField(default=0, help_text='Defines how much points will be GIVEN from the user on SUCCESS bet on match result.', validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(5000)])),
                ('phase', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='bet_points', to='events.eventphase')),
            ],
        ),
    ]
