# Generated by Django 3.2.3 on 2021-05-18 00:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('events', '0010_alter_eventphases_phase_match_states'),
    ]

    operations = [
        migrations.AlterField(
            model_name='eventphases',
            name='phase_match_states',
            field=models.ManyToManyField(to='events.EventMatchStates'),
        ),
    ]