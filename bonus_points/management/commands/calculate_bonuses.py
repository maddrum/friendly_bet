from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from bonus_points.calculators.calculators import *
from bonus_points.models import BonusDescription
from matches.models import Matches


class Command(BaseCommand):

    def handle(self, *args, **options):
        users = get_user_model().objects.all()
        all_bonuses = BonusDescription.objects.filter(bonus_active=True)

        # 1 Calculate all auto bonuses
        auto_bonuses = all_bonuses.filter(auto_bonus=True)

        for bonus in auto_bonuses:
            first_match = Matches.objects.filter(phase__event=bonus.event).order_by('match_number').first()
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
