from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from bonus_points.calculators.calculators import *
from bonus_points.models import BonusDescription, BonusUserPrediction, BonusUserScore
from matches.models import Match
from django.db import transaction


class Command(BaseCommand):

    @transaction.atomic
    def handle(self, *args, **options):
        users = get_user_model().objects.all()

        # 1 Calculate all auto bonuses
        auto_bonuses = BonusDescription.objects.filter(bonus_active=True, auto_bonus=True)
        for bonus in auto_bonuses:
            first_match = Match.objects.filter(phase__event=bonus.event).order_by('match_number').first()
            event_total_matches = bonus.event.event_total_matches
            if bonus.auto_bonus_calculator_function_name is None \
                    or len(bonus.auto_bonus_calculator_function_name) == 0:
                self.stdout.write(self.style.ERROR(f'[ERROR] skipped bonus:{bonus}'))
                continue
            calculator = eval(bonus.auto_bonus_calculator_function_name)
            for user in users:
                result = calculator(user, bonus, first_match=first_match, total_matches=event_total_matches)
                if result:
                    self.stdout.write(self.style.SUCCESS(f'[INFO] {result}'))

        # 2 Calculate other bonuses
        all_bonus_user_predictions = BonusUserPrediction.objects.all().prefetch_related('bonus', 'user')
        for prediction in all_bonus_user_predictions:
            if prediction.bonus.correct_answer is not None \
                    and prediction.user_prediction == prediction.bonus.correct_answer:
                bonus_score, created = BonusUserScore.objects.get_or_create(prediction=prediction)
                bonus_score.points_gained = prediction.bonus.points
                bonus_score.summary_text = f'"{prediction.bonus.name}" | познал: "{prediction.bonus.correct_answer}" |' \
                                           f' Взел: {prediction.bonus.points} точки.'
                bonus_score.save()
                self.stdout.write(self.style.SUCCESS(f'[INFO] Added {prediction.bonus.points} to '
                                                     f'{prediction.user} for {prediction.bonus.name}'))
