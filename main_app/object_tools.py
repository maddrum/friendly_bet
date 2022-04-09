import random

from django.contrib.auth import get_user_model
from django.core.management import call_command
from django.db import transaction

from accounts.model_factories import UserFactory
from events.model_factories import EventFactory, EventGroupFactory, EventMatchStateFactory, EventPhaseFactory, \
    PhaseBetPointFactory, TeamFactory
from events.models import EventGroup, EventMatchState, EventPhase
from events.settings import MATCH_STATE_GUEST, MATCH_STATE_HOME, MATCH_STATE_PENALTIES_GUEST, \
    MATCH_STATE_PENALTIES_HOME, MATCH_STATE_TIE, MATCH_STATES, PHASE_SELECTOR
from matches.model_factories import generate_group_matches, MatchFactory
from matches.models import Match
from predictions.model_factories import UserPredictionFactory
from predictions.models import BetAdditionalPoint

# todo - remove
call_command('migrate')
if not get_user_model().objects.filter(is_superuser=True).exists():
    admin_user = get_user_model().objects.create(username='maddrum')
    admin_user.set_password('qqwerty123')
    admin_user.is_superuser = True
    admin_user.is_staff = True
    admin_user.save()
    print(admin_user)


def generate_valid_goals_by_match_state(match_state):
    goals_home = random.randint(1, 10)
    if match_state in [MATCH_STATE_HOME, MATCH_STATE_PENALTIES_HOME]:
        goals_guest = goals_home - 1
    elif match_state in [MATCH_STATE_GUEST, MATCH_STATE_PENALTIES_GUEST]:
        goals_guest = goals_home + 1
    elif match_state == MATCH_STATE_TIE:
        goals_guest = goals_home
    else:
        return None, None

    return goals_home, goals_guest


def create_valid_prediction():
    iter_items = [item[0] for item in MATCH_STATES if
                  item[0] not in [MATCH_STATE_PENALTIES_HOME, MATCH_STATE_PENALTIES_GUEST]]
    match_state = random.choice(iter_items)
    event_match_state = EventMatchState.objects.get(match_state=match_state)
    pk = event_match_state.pk

    goals_home, goals_guest = generate_valid_goals_by_match_state(match_state=match_state)
    apply_match_state = random.choice([True, False])
    apply_result = random.choice([True, False])

    return match_state, pk, goals_home, goals_guest, event_match_state, apply_match_state, apply_result


def create_invalid_prediction():
    match_state, pk, goals_home, goals_guest, \
    event_match_state, apply_match_state, apply_result = create_valid_prediction()

    if match_state == MATCH_STATE_TIE:
        goals_home += 1
    temp_goals_home = goals_home
    goals_home = goals_guest
    goals_guest = temp_goals_home

    return match_state, pk, goals_home, goals_guest, event_match_state, apply_match_state, apply_result


@transaction.atomic
def initialize_event(groups=8):
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


@transaction.atomic
def add_user_predictions(event, users=5):
    for item in range(users):
        temp_user = UserFactory()
        temp_user.set_password('qqwerty123')
        temp_user.save()

    for user in get_user_model().objects.all():
        for match in Match.objects.filter(phase__event=event):
            prediction_data = create_valid_prediction()
            prediction = UserPredictionFactory(
                user=user,
                match=match,
                match_state=prediction_data[4],
                goals_home=prediction_data[2],
                goals_guest=prediction_data[3],
            )
            prediction.save()

            add_points_obj, created = BetAdditionalPoint.objects.get_or_create(prediction=prediction)
            phase_points = match.phase.bet_points
            add_points_obj.apply_match_state = random.choice([True, False])
            add_points_obj.apply_result = random.choice([True, False])
            add_points_obj.points_match_state_to_take = phase_points.points_state
            add_points_obj.points_match_state_to_give = phase_points.return_points_state
            add_points_obj.points_result_to_take = phase_points.points_result
            add_points_obj.points_result_to_give = phase_points.return_points_result
            add_points_obj.save()
