import datetime

import factory
from django.utils import timezone
from django.utils.timezone import make_aware
from faker import Faker

from .models import Event, EventGroup, EventMatchState, EventPhase, PhaseBetPoint, Team
from .settings import (
    MATCH_STATE_PENALTIES_GUEST,
    MATCH_STATE_PENALTIES_HOME,
    MATCH_STATE_TIE,
    MATCH_STATES,
    PHASE_GROUP,
    PHASE_SELECTOR,
)

fake = Faker()


def get_start_datetime(plus_days=1):
    start_date = timezone.now().date() + timezone.timedelta(days=plus_days)
    time = datetime.time(18, 30, 0)
    start_datetime = make_aware(timezone.datetime.combine(start_date, time))
    return start_datetime


class EventFactory(factory.Factory):
    class Meta:
        model = Event

    event_name = factory.Faker("company", locale="bg_BG")
    event_start_date = factory.LazyFunction(get_start_datetime)
    event_end_date = factory.LazyAttribute(
        lambda o: o.event_start_date + datetime.timedelta(days=30)
    )
    event_total_matches = 8

    @factory.lazy_attribute
    def event_name(self):
        words = " ".join([fake.word() for item in range(2)]) + " cup"
        return words.title()


class EventGroupFactory(factory.Factory):
    class Meta:
        model = EventGroup

    event = factory.SubFactory(EventFactory)
    event_group = factory.Sequence(lambda n: "GROUP-%s" % str(n + 1))


class EventMatchStateFactory(factory.Factory):
    class Meta:
        model = EventMatchState

    event = factory.SubFactory(EventFactory)
    match_state = factory.Sequence(lambda n: MATCH_STATES[n][0])


class EventPhaseFactory(factory.Factory):
    class Meta:
        model = EventPhase

    event = factory.SubFactory(EventFactory)
    phase = factory.Sequence(lambda n: PHASE_SELECTOR[n][0])
    multiplier = factory.Sequence(lambda n: n + 1)

    @factory.post_generation
    def phase_match_states(self, create, extracted, **kwargs):
        self.save()
        if self.phase == PHASE_GROUP:
            for state in EventMatchState.objects.all().exclude(
                match_state__in=[
                    MATCH_STATE_PENALTIES_HOME,
                    MATCH_STATE_PENALTIES_GUEST,
                ]
            ):
                self.phase_match_states.add(state)
        else:
            for state in EventMatchState.objects.all().exclude(
                match_state=MATCH_STATE_TIE
            ):
                self.phase_match_states.add(state)


class TeamFactory(factory.Factory):
    class Meta:
        model = Team

    group = factory.SubFactory(EventGroupFactory)

    @factory.lazy_attribute
    def name(self):
        name = fake.country()
        while Team.objects.filter(name=name).exists():
            name = fake.country()
            if Team.objects.filter(name=name).exists():
                continue
            break
        return name


class PhaseBetPointFactory(factory.Factory):
    class Meta:
        model = PhaseBetPoint

    phase = factory.SubFactory(EventPhaseFactory)
    points_state = factory.Sequence(lambda n: (n + 2) * (n + 1))
    points_result = factory.Sequence(lambda n: (n + 3) * (n + 1))

    @factory.lazy_attribute
    def return_points_state(self):
        return self.points_state + 10

    @factory.lazy_attribute
    def return_points_result(self):
        return self.points_result + 20
