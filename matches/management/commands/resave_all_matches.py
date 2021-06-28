from django.core.management.base import BaseCommand

from matches.models import MatchResult


class Command(BaseCommand):
    def handle(self, *args, **options):
        all_results = MatchResult.objects.all()
        for result in all_results:
            result.save()
            self.stdout.write(self.style.SUCCESS(f'[INFO]Saved: {result}'))
