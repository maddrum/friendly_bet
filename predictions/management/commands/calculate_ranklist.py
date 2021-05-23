from django.core.management.base import BaseCommand

from predictions.prediction_calculators import calculate_ranklist


class Command(BaseCommand):
    def handle(self, *args, **options):
        calculate_ranklist()
        self.stdout.write(self.style.SUCCESS('[INFO]Ranklist updated'))
