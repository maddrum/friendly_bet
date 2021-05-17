from django import forms

from predictions.models import UserPredictions


class PredictionForm(forms.ModelForm):
    class Meta:
        model = UserPredictions
        fields = ('match_state', 'goals_home', 'goals_guest')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['goals_home'].widget.attrs = {
            'style': "font-size: 17px;width: 200px"
        }
        self.fields['goals_guest'].widget.attrs = {
            'style': "font-size: 17px;width: 200px"
        }

    def clean(self):
        cleaned_data = super().clean()

        return cleaned_data
