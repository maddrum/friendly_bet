import random
from dataclasses import dataclass

from django.contrib.auth import get_user_model
from django.db import transaction

from accounts.model_factories import UserFactory
from events.models import EventMatchState
from events.settings import (
    MATCH_STATE_GUEST,
    MATCH_STATE_HOME,
    MATCH_STATE_PENALTIES_GUEST,
    MATCH_STATE_PENALTIES_HOME,
    MATCH_STATE_TIE,
    MATCH_STATES,
)
from matches.models import Match
from predictions.model_factories import UserPredictionFactory
from predictions.models import BetAdditionalPoint


@dataclass
class PredictionDTO:
    match_state: str
    pk: int
    goals_home: int
    goals_guest: int
    event_match_state: EventMatchState
    apply_match_state: bool
    apply_result: bool


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


def create_valid_prediction() -> PredictionDTO:
    iter_items = [
        item[0]
        for item in MATCH_STATES
        if item[0] not in [MATCH_STATE_PENALTIES_HOME, MATCH_STATE_PENALTIES_GUEST]
    ]
    match_state = random.choice(iter_items)
    event_match_state = EventMatchState.objects.get(match_state=match_state)
    pk = event_match_state.pk

    goals_home, goals_guest = generate_valid_goals_by_match_state(
        match_state=match_state
    )
    apply_match_state = random.choice([True, False])
    apply_result = random.choice([True, False])
    prediction_dto = PredictionDTO(
        match_state=match_state,
        pk=pk,
        goals_home=goals_home,
        goals_guest=goals_guest,
        event_match_state=event_match_state,
        apply_match_state=apply_match_state,
        apply_result=apply_result,
    )

    return prediction_dto


def create_invalid_prediction():
    prediction_dto = create_valid_prediction()

    if prediction_dto.match_state == MATCH_STATE_TIE:
        prediction_dto.goals_home += 1
    temp_goals_home = prediction_dto.goals_home
    prediction_dto.goals_home = prediction_dto.goals_guest
    prediction_dto.goals_guest = temp_goals_home

    prediction_dto = PredictionDTO(
        match_state=prediction_dto.match_state,
        pk=prediction_dto.pk,
        goals_home=prediction_dto.goals_home,
        goals_guest=prediction_dto.goals_guest,
        event_match_state=prediction_dto.event_match_state,
        apply_match_state=prediction_dto.apply_match_state,
        apply_result=prediction_dto.apply_result,
    )

    return prediction_dto


@transaction.atomic
def add_user_predictions(event, users=5):
    for item in range(users):
        temp_user = UserFactory()
        temp_user.set_password("qqwerty123")
        temp_user.save()

    for user in get_user_model().objects.all():
        for match in Match.objects.filter(phase__event=event):
            prediction_data = create_valid_prediction()
            prediction = UserPredictionFactory(
                user=user,
                match=match,
                match_state=prediction_data.event_match_state,
                goals_home=prediction_data.goals_home,
                goals_guest=prediction_data.goals_guest,
            )
            prediction.save()

            add_points_obj, created = BetAdditionalPoint.objects.get_or_create(
                prediction=prediction
            )
            phase_points = match.phase.bet_points
            add_points_obj.apply_match_state = random.choice([True, False])
            add_points_obj.apply_result = random.choice([True, False])
            add_points_obj.points_match_state_to_take = phase_points.points_state
            add_points_obj.points_match_state_to_give = phase_points.return_points_state
            add_points_obj.points_result_to_take = phase_points.points_result
            add_points_obj.points_result_to_give = phase_points.return_points_result
            add_points_obj.save()
