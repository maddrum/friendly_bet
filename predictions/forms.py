from django import forms

from predictions.models import UserPredictions
from events.settings import MATCH_STATE_HOME, MATCH_STATE_GUEST, MATCH_STATE_PENALTIES_HOME, \
    MATCH_STATE_PENALTIES_GUEST, MATCH_STATE_TIE
from django.core.exceptions import ValidationError


class PredictionForm(forms.ModelForm):
    class Meta:
        model = UserPredictions
        fields = ('match_state', 'goals_home', 'goals_guest')

    def __init__(self, phase=None, home_team=None, guest_team=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.home_team = home_team
        self.guest_team = guest_team
        self.fields['goals_home'].widget.attrs = {
            'class': 'goals-input',
            'required': 'required',
        }
        self.fields['goals_guest'].widget.attrs = {
            'class': 'goals-input',
            'required': 'required',
        }
        self.fields['match_state'].widget.attrs = {
            'class': 'match-select',
            'required': 'required',
        }

        MATCH_STATE_OPTIONS = {
            MATCH_STATE_HOME: f'ПОБЕДА за {self.home_team}',
            MATCH_STATE_GUEST: f'ПОБЕДА за {self.guest_team}',
            MATCH_STATE_PENALTIES_HOME: f'ПОБЕДА за {self.home_team} след ДУЗПИ',
            MATCH_STATE_PENALTIES_GUEST: f'ПОБЕДА за {self.guest_team} след ДУЗПИ',
            MATCH_STATE_TIE: 'Тики-така, скучен РАВЕН'
        }
        try:
            self.fields['match_state'].queryset = phase.phase_match_states.all()
        except AttributeError:
            pass

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
        if 'goals_home' not in cleaned_data \
                or 'goals_guest' not in cleaned_data \
                or 'match_state' not in cleaned_data:
            raise ValidationError('Нещо не е наред с попълнените данни...')
        if cleaned_data['goals_home'] < 0 or cleaned_data['goals_guest'] < 0:
            raise ValidationError(
                'Както би казал Домусата: Или си олигофрен, или не знам. '
                'Къде го видя тоя мач с ОТРИЦАТЕЛНИ голове бе, обясни ми, къде го видя!')
        if cleaned_data['match_state'].match_state == MATCH_STATE_TIE:
            if cleaned_data['goals_home'] != cleaned_data['goals_guest']:
                raise ValidationError(
                    'ГРЕДА! Дал си, че ще е равен ама головете на едните на са колкото головете на другите')

        elif cleaned_data['match_state'].match_state == MATCH_STATE_HOME or \
                cleaned_data['match_state'].match_state == MATCH_STATE_PENALTIES_HOME:
            if cleaned_data['goals_home'] <= cleaned_data['goals_guest']:
                raise ValidationError(
                    f'ГРЕДА! Дал си, че ще е победа за {self.home_team} ама головете им '
                    f'са по-малко или в краен случай равни на головете на {self.guest_team}.')

        elif cleaned_data['match_state'].match_state == MATCH_STATE_GUEST or \
                cleaned_data['match_state'].match_state == MATCH_STATE_PENALTIES_GUEST:
            if cleaned_data['goals_home'] >= cleaned_data['goals_guest']:
                raise ValidationError(
                    f'ГРЕДА! Дал си, че ще е победа за {self.guest_team} ама головете им '
                    f'са по-малко или в краен случай равни на головете на {self.home_team}.')
        return cleaned_data
