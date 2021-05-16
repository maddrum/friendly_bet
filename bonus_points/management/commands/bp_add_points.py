from bonus_points.models import UserBonusSummary
from matches.models import UserScore
from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.core.exceptions import ObjectDoesNotExist


class Command(BaseCommand):
    # adds Bonus Points to overall user points for the final ranklist
    def handle(self, *args, **options):
        users = get_user_model().objects.all()
        for user in users:
            try:
                bonus_points = UserBonusSummary.objects.get(user=user).total_bonus_points
            except ObjectDoesNotExist:
                bonus_points = 0
            try:
                ranklist_object = UserScore.objects.get(user_id=user)
            except ObjectDoesNotExist:
                ranklist_object = None
            if bonus_points == 0 and ranklist_object is None:
                continue
            if ranklist_object is not None and not ranklist_object.bonus_points_added:
                ranklist_object.points += bonus_points
                ranklist_object.bonus_points_added = True
                ranklist_object.save()
            elif bonus_points != 0 and ranklist_object is None:
                print(f'{user} has bonus points only!')
                new = UserScore(user_id=user, points=bonus_points, bonus_points_added=True)
                new.save()
            else:
                print(f'Points for {user} already added!')
                continue
        self.stdout.write(self.style.SUCCESS('Successfully added bonus points'))
