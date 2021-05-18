from django import forms

from predictions.models import UserPredictions
from events.settings import MATCH_STATE_HOME, MATCH_STATE_GUEST, MATCH_STATE_PENALTIES_HOME, \
    MATCH_STATE_PENALTIES_GUEST, MATCH_STATE_TIE


class PredictionForm(forms.ModelForm):
    class Meta:
        model = UserPredictions
        fields = ('match_state', 'goals_home', 'goals_guest')

    def __init__(self, phase, home_team, guest_team, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['goals_home'].widget.attrs = {
            'style': "font-size: 17px;width: 200px"
        }
        self.fields['goals_guest'].widget.attrs = {
            'style': "font-size: 17px;width: 200px"
        }

        MATCH_STATE_OPTIONS = {
            MATCH_STATE_HOME: f'ПОБЕДА за {home_team}',
            MATCH_STATE_GUEST: f'ПОБЕДА за {guest_team}',
            MATCH_STATE_PENALTIES_HOME: f'ПОБЕДА за {home_team} след дузпи',
            MATCH_STATE_PENALTIES_GUEST: f'ПОБЕДА за {guest_team} след дузпи',
            MATCH_STATE_TIE: 'Тики-така, скучен РАВЕН'
        }
        self.fields['match_state'].queryset = phase.phase_match_states.all()

        result_names = []
        for choice in self.fields['match_state'].choices:
            try:
                match_state = choice[0].instance.match_state
            except AttributeError:
                match_state = choice[0]
            new_string = MATCH_STATE_OPTIONS.get(match_state, choice[1])
            result_names.append((choice[0], new_string))

        self.fields['match_state'].choices = result_names

    def clean(self):
        cleaned_data = super().clean()

        return cleaned_data
