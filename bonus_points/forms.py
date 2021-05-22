from django import forms
from django.forms.widgets import Select

from events.models import Teams


class InputAllTeamsForm(forms.Form):
    countries = [(item.name, item.name) for item in Teams.objects.all()]

    user_prediction = forms.CharField(widget=Select(choices=countries), label='Избери отбор')


class InputNumberForm(forms.Form):
    user_prediction = forms.IntegerField(label='Въведи число')


class InputChoicesForm(forms.Form):
    user_prediction = forms.CharField(label='Избери едно:')

    def __init__(self, choices, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.choices = choices
        self.choices_list = [(item, item) for item in self.choices]
        self.fields['user_prediction'].widget = Select(choices=self.choices_list)
