from django import forms
from matches.models import Countries
from django.forms.widgets import Select


class SelectAllCountriesForm(forms.Form):
    countries = [(item.name, item.name) for item in Countries.objects.all()]
    user_prediction = forms.CharField(widget=Select(choices=countries), label='Избери държава')


class InputTextForm(forms.Form):
    user_prediction = forms.CharField(label='Напиши твоята прогноза')


class InputNumberForm(forms.Form):
    user_prediction = forms.IntegerField(label='Въведи номер')


class InputSomeChoicesForm(forms.Form):
    def __init__(self, *args, **kwargs):
        self.choices = kwargs.pop('choices')
        super(InputSomeChoicesForm, self).__init__(*args, **kwargs)
        self.choices_list = [(item, item) for item in self.choices['choices']]
        self.fields['user_prediction'].widget = Select(choices=self.choices_list)

    user_prediction = forms.CharField(label='Избери едно:')
