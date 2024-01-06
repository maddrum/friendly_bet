import random

from django.contrib.auth import get_user_model
from django.core.management import call_command
from django.core.management.base import BaseCommand

from events.settings import PHASE_GROUP
from matches.model_factories import MatchResultFactory
from matches.models import Match
from matches.tools import initialize_matches
from predictions.prediction_calculators import calculate_ranklist, calculate_user_predictions
from predictions.tools import add_user_predictions, generate_valid_goals_by_match_state


class Command(BaseCommand):
    def handle(self, *args, **options):
        call_command("flush")
        call_command("migrate")

        event = initialize_matches()
        add_user_predictions(event=event, users=50)
        phase = event.event_phases.filter(phase=PHASE_GROUP).first()

        for match in Match.objects.filter(phase__event=event, phase=phase):
            self.stdout.write(self.style.SUCCESS(f"[INFO] Trying to add match {str(match)} ... "))
            user_guessed = random.choice(get_user_model().objects.all())
            prediction = user_guessed.predictions.get(match=match)
            result = MatchResultFactory(
                match=match,
                match_state=prediction.match_state,
                score_home=prediction.goals_home,
                score_guest=prediction.goals_guest,
                match_is_over=True,
            )

            calculate_user_predictions(instance_id=result.pk)
            calculate_ranklist(instance_id=result.pk)

        self.stdout.write(self.style.SUCCESS("[INFO] generated random data"))
