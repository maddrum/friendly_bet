from bonus_points.models import BonusDescription, BonusUserAutoPoints
from matches.models import UserPredictions
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model


class Command(BaseCommand):
    # calculate bonus points for contest "give prediction for 36 matches" /id = 1/
    def handle(self, *args, **options):
        all_users = get_user_model().objects.all()
        bonus_desc_object = BonusDescription.objects.get(id=1)
        needed_count = int(bonus_desc_object.correct_answer)
        points = bonus_desc_object.points
        # delete existing objects
        delete_current_objects = BonusUserAutoPoints.objects.filter(auto_user_bonus_name=bonus_desc_object)
        for item in delete_current_objects:
            item.delete()
        # check for all users
        for item in all_users:
            user_predictions_count = UserPredictions.objects.filter(user_id=item, match__phase='group_phase').count()
            if user_predictions_count >= needed_count:
                summary_text = f"Ти си дал {user_predictions_count} прогнози, при необходими {needed_count} за груповата фаза. \\n Tи спечели {points} точки за това."
                user_obj = BonusUserAutoPoints(user=item, auto_user_bonus_name=bonus_desc_object,
                                               points_gained=points, summary_text=summary_text)
                user_obj.save()
        self.stdout.write(self.style.SUCCESS('Successfully updated bonus 1'))
