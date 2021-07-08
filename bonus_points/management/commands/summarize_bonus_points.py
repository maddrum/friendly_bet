from django.core.management.base import BaseCommand
from django.db import transaction

from bonus_points.models import AutoBonusUserScore, BonusUserScore, UserBonusSummary


class Command(BaseCommand):

    @transaction.atomic
    def handle(self, *args, **options):
        for item in UserBonusSummary.objects.all():
            item.total_bonus_points = 0
            item.total_summary = ''
            item.save()

        for bonus_points in BonusUserScore.objects.all().prefetch_related('prediction', 'prediction__user',
                                                                          'prediction__bonus__event'):
            user = bonus_points.prediction.user
            bonus_summary_obj, created = UserBonusSummary.objects.get_or_create(user=user,
                                                                                event=bonus_points.prediction.bonus.event)
            bonus_summary_obj.total_bonus_points += bonus_points.points_gained
            bonus_summary_obj.total_summary += (bonus_points.summary_text + '\n')
            bonus_summary_obj.save()
            self.stdout.write(self.style.SUCCESS(f'[INFO] Added {bonus_points}'))

        for bonus_points in AutoBonusUserScore.objects.all().prefetch_related('user', 'bonus', 'bonus__event'):
            bonus_summary_obj, created = UserBonusSummary.objects.get_or_create(user=bonus_points.user,
                                                                                event=bonus_points.bonus.event)
            bonus_summary_obj.total_bonus_points += bonus_points.points_gained
            bonus_summary_obj.total_summary += (bonus_points.summary_text + '\n')
            bonus_summary_obj.save()
            self.stdout.write(self.style.SUCCESS(f'[INFO] Added {bonus_points}'))

        self.stdout.write(self.style.SUCCESS('[INFO] Successfully summarized bonus points'))
