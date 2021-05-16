from django.core.management.base import BaseCommand
from matches.models import UserPredictions
import datetime


class Command(BaseCommand):
    def handle(self, *args, **options):
        all_predictions = UserPredictions.objects.all()
        for item in all_predictions:
            time_delta_creation_last_edit = item.last_edit - item.creation_time
            if time_delta_creation_last_edit.seconds != 0:
                print('--------------------------------------')
                print(item)
                print(f'created: {item.creation_time}')
                print(f'edited: {item.last_edit}')
                print(f'Time Delta: {time_delta_creation_last_edit}')
            if item.match.match_number >= 45:
                if item.match.match_start_time_utc < item.last_edit or item.match.match_start_time_utc < item.last_edit:
                    print('|||||||||||CHEATER!!!!||||||||||')
                    print(item)
                    print(f'created: {item.creation_time}')
                    print(f'edited: {item.last_edit}')
                    print(f'match start time: {item.match.match_start_time_utc}')
        print()
        self.stdout.write(self.style.SUCCESS('Script was ran successfully!'))
