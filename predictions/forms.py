from django import forms

from predictions.models import UserPredictions


class PredictionForm(forms.ModelForm):
    class Meta:
        model = UserPredictions
        fields = ('match_state', 'goals_home', 'goals_guest')
        labels = {
            'prediction_match_state': 'Изход от двубоя',
            'prediction_goals_home': 'Голове домакин',
            'prediction_goals_guest': 'Голове гост',
        }

    def clean(self):
        cleaned_data = super().clean()
        return cleaned_data
