from django import forms

from predictions.models import UserPredictions


class UpdatePredictionForm(forms.ModelForm):
    class Meta:
        model = UserPredictions
        fields = ('prediction_match_state', 'prediction_goals_home', 'prediction_goals_guest')
        labels = {
            'prediction_match_state': 'Изход от двубоя',
            'prediction_goals_home': 'Голове домакин',
            'prediction_goals_guest': 'Голове гост',
        }
