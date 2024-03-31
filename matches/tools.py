from django.db import transaction

from events.model_factories import (
    EventFactory,
    EventGroupFactory,
    EventMatchStateFactory,
    EventPhaseFactory,
    PhaseBetPointFactory,
    TeamFactory,
)
from events.models import Event, EventGroup, EventPhase
from events.settings import MATCH_STATES, PHASE_SELECTOR
from matches.model_factories import generate_group_matches, MatchFactory
from matches.models import Match, MatchResult


@transaction.atomic
def initialize_matches(groups=8) -> "Event":
    EventFactory.reset_sequence()
    event = EventFactory()

    # groups
    EventGroupFactory.reset_sequence()
    for item in range(groups):
        EventGroupFactory(event=event)

    # states
    EventMatchStateFactory.reset_sequence()
    for item in MATCH_STATES:
        EventMatchStateFactory(event=event)

    # phases
    EventPhaseFactory.reset_sequence()
    for item in PHASE_SELECTOR:
        EventPhaseFactory(event=event)

    # teams
    TeamFactory.reset_sequence()
    for group in EventGroup.objects.filter(event=event):
        for item in range(4):
            TeamFactory(group=group)

    # bet points
    PhaseBetPointFactory.reset_sequence()
    for phase in EventPhase.objects.filter(event=event):
        PhaseBetPointFactory(phase=phase)

    # matches
    MatchFactory.reset_sequence()
    for group in EventGroup.objects.filter(event=event):
        for match in generate_group_matches(group):
            MatchFactory(
                home=match[0],
                guest=match[1],
                phase=EventPhase.objects.filter(event=event).first(),
            )

    return event


def create_match_result(match: "Match") -> "MatchResult":
    match_result, created = MatchResult.objects.get_or_create(
        match=match, match_state=match.phase.event.event_match_states.all().first()
    )

    return match_result
