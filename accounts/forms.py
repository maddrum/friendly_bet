from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import get_user_model
from django import forms
from matches.models import UserPredictions


class AccountRegisterForm(UserCreationForm):
    class Meta:
        model = get_user_model()
        fields = ('username', 'password1', 'password2')


class UpdatePredictionForm(forms.ModelForm):
    class Meta:
        model = UserPredictions
        fields = ('prediction_match_state', 'prediction_goals_home', 'prediction_goals_guest')
        labels = {
            'prediction_match_state': 'Изход от двубоя',
            'prediction_goals_home': 'Голове домакин',
            'prediction_goals_guest': 'Голове гост',
        }
