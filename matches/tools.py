from django.db import transaction

from events.model_factories import EventFactory, EventGroupFactory, EventMatchStateFactory, EventPhaseFactory, \
    PhaseBetPointFactory, TeamFactory
from events.models import EventGroup, EventPhase
from events.settings import MATCH_STATES, PHASE_SELECTOR
from matches.model_factories import generate_group_matches, MatchFactory


@transaction.atomic
def initialize_matches(groups=8):
    EventFactory.reset_sequence()
    event = EventFactory()
    event.save()

    # groups
    EventGroupFactory.reset_sequence()
    for item in range(groups):
        group = EventGroupFactory(event=event)
        group.save()

    # states
    EventMatchStateFactory.reset_sequence()
    for item in MATCH_STATES:
        state = EventMatchStateFactory(event=event)
        state.save()

    # phases
    EventPhaseFactory.reset_sequence()
    for item in PHASE_SELECTOR:
        phase = EventPhaseFactory(event=event)
        phase.save()

    # teams
    TeamFactory.reset_sequence()
    for group in EventGroup.objects.filter(event=event):
        for item in range(4):
            team = TeamFactory(group=group)
            team.save()

    # bet points
    PhaseBetPointFactory.reset_sequence()
    for phase in EventPhase.objects.filter(event=event):
        bet_points = PhaseBetPointFactory(phase=phase)
        bet_points.save()

    # matches
    MatchFactory.reset_sequence()
    for group in EventGroup.objects.filter(event=event):
        for match in generate_group_matches(group):
            match = MatchFactory(home=match[0], guest=match[1], phase=EventPhase.objects.filter(event=event).first())
            match.save()

    return event
