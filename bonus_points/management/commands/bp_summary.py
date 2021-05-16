from bonus_points.models import BonusUserPrediction, UserBonusSummary, BonusUserAutoPoints
from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    # makes summary of points for all users
    def handle(self, *args, **options):
        # delete all existing bonuses
        UserBonusSummary.objects.all().delete()
        # calculate all points for user
        all_users = get_user_model().objects.all()
        for item in all_users:
            points = 0
            summary_text = ''
            auto_points_all = BonusUserAutoPoints.objects.filter(user=item)
            non_auto_points_all = BonusUserPrediction.objects.filter(user=item)
            for auto_p in auto_points_all:
                if auto_p.points_gained != 0:
                    points += auto_p.points_gained
                    summary_text = summary_text + f' От играта \"{auto_p.auto_user_bonus_name}\" получи: {auto_p.points_gained} точки \n'
            for non_ap in non_auto_points_all:
                if non_ap.points_gained != 0:
                    points += non_ap.points_gained
                    summary_text = summary_text + f' От играта \"{non_ap.user_bonus_name}\" получи: {non_ap.points_gained} точки \n'
            # save to database
            if points == 0:
                continue
            user_summary = UserBonusSummary(user=item, total_bonus_points=points, total_summary=summary_text)
            user_summary.save()

        self.stdout.write(self.style.SUCCESS('Successfully summarized bonuses'))
