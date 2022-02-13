from django.core.management.base import BaseCommand
from django.db import transaction

from bonus_points.models import UserBonusSummary
from predictions.models import UserScore


class Command(BaseCommand):

    @transaction.atomic
    def handle(self, *args, **options):
        for bonus_summary in UserBonusSummary.objects.all().prefetch_related('user', 'event'):
            ranklist_object, created = UserScore.objects.get_or_create(user=bonus_summary.user,
                                                                       event=bonus_summary.event)
            if ranklist_object.bonus_points_added:
                self.stdout.write(self.style.WARNING(f'[INFO] skipped for {bonus_summary.user}'))
                continue
            ranklist_object.bonus_points_added = True
            ranklist_object.points += bonus_summary.total_bonus_points
            ranklist_object.save()
            self.stdout.write(self.style.SUCCESS(f'[INFO] Added bonus points for {bonus_summary.user}'))

        self.stdout.write(self.style.SUCCESS('[INFO] Successfully added bonus points'))
