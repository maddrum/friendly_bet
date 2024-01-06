import datetime

import factory
from django.utils import timezone
from faker import Faker

from events.model_factories import EventPhaseFactory, TeamFactory
from events.models import EventGroup, Team
from matches.models import Match

fake = Faker()
DAILY_MATCHES = 4


def generate_group_matches(group):
    matches = []
    teams = Team.objects.filter(group=group).order_by("pk")
    for team in teams:
        for other_team in teams:
            if other_team.pk > team.pk:
                matches.append((team, other_team))
    matches = [matches[0], matches[5], matches[1], matches[4], matches[2], matches[3]]
    return matches


class MatchFactory(factory.Factory):
    class Meta:
        model = Match

    home = factory.SubFactory(TeamFactory)
    guest = factory.SubFactory(TeamFactory)
    phase = factory.SubFactory(EventPhaseFactory)
    match_number = factory.Sequence(lambda n: n + 1)

    @factory.lazy_attribute
    def match_start_time(self):
        group = self.home.group
        event = group.event
        matches = generate_group_matches(group)
        looking_tuple = (
            (self.home, self.guest)
            if self.home.pk < self.guest.pk
            else (self.guest, self.home)
        )
        match_series = matches.index(looking_tuple) // 2
        group_series = [item for item in EventGroup.objects.all().order_by("pk")].index(
            group
        ) // 2
        group_day_step = DAILY_MATCHES
        days = match_series * group_day_step + group_series
        start_date = event.event_start_date + timezone.timedelta(days=days)

        current_counter = (
            Match.objects.filter(
                match_start_time__gte=datetime.datetime.combine(
                    start_date, datetime.time(0, 0, 0)
                ),
                match_start_time__lte=datetime.datetime.combine(
                    start_date, datetime.time(23, 59, 59)
                ),
            ).count()
            + 1
        )
        add_hours = ((current_counter - 1) // 2) * 2
        start_time = datetime.time(16, 30)
        match_start = datetime.datetime.combine(
            start_date, start_time
        ) + datetime.timedelta(hours=add_hours)
        return match_start
