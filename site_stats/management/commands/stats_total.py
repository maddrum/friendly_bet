from matches.models import UserPredictions
from site_stats.models import TotalStats, UserGuessesNumber
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model


class Command(BaseCommand):
    # calculate total bonus points
    def handle(self, *args, **options):
        users = get_user_model().objects.all()
        all_predictions = UserPredictions.objects.all()
        total_predictions = all_predictions.count()
        points = 0
        user_guessed_matches = {user.username: 0 for user in users}
        user_guessed_results = {user.username: 0 for user in users}
        # fill user_guessed_matches and and user_guessed_results
        for item in all_predictions:
            points += item.points_gained
            summary_text = item.prediction_note
            guessed_match_state_number = len(summary_text.split("2.")) - 1
            guessed_match_result_number = len(summary_text.split("3.")) - 1
            username = item.user_id.username
            user_guessed_matches[username] += guessed_match_state_number
            user_guessed_results[username] += guessed_match_result_number
        # write user stats - guessed matches and guessed results
        for user in users:
            username = user.username
            user_matches = user_guessed_matches[username]
            user_results = user_guessed_results[username]
            object_count = UserGuessesNumber.objects.filter(user=user).count()
            if object_count == 0:
                new_object = UserGuessesNumber(user=user, guessed_matches=user_matches, guessed_results=user_results)
                new_object.save()
            else:
                update_object = UserGuessesNumber.objects.get(user=user.id)
                update_object.guessed_matches = user_matches
                update_object.guessed_results = user_results
                update_object.save()
        sum_matches = sum(user_guessed_matches.values())
        sum_results = sum(user_guessed_results.values())
        new_stats_object = TotalStats(total_predictions=total_predictions, total_points_gained=points,
                                      total_match_states_guessed=sum_matches, total_match_results_guessed=sum_results)
        new_stats_object.save()
        self.stdout.write(self.style.SUCCESS('Successfully updated stats'))
