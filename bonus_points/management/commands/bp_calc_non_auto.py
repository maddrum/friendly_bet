from bonus_points.models import BonusDescription, BonusUserPrediction
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    # calculate bonus points for contest all non auto / participate_link = True/
    def handle(self, *args, **options):
        all_contests = [item for item in BonusDescription.objects.filter(participate_link=True)]
        # writes all non-auto predictions
        for item in all_contests:
            user_predictions = BonusUserPrediction.objects.filter(user_bonus_name=item)
            correct_answer = item.correct_answer
            if correct_answer == None:
                continue
            points = item.points
            for user_item in user_predictions:
                if user_item.user_prediction == correct_answer:
                    user_item.points_gained = points
                    summary_text = f'Ти позна и получи {points} точки'
                    user_item.summary_text = summary_text
                    user_item.save()
                else:
                    user_item.points_gained = 0
                    summary_text = f'Ти не успя да познаеш.'
                    user_item.summary_text = summary_text
                    user_item.save()
        self.stdout.write(self.style.SUCCESS('Successfully updated non auto bonuses'))
