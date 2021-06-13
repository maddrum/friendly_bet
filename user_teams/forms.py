import unidecode
from django import forms
from django.utils.text import slugify

from user_teams.models import UserTeam


class CreateUpdateTeamForm(forms.ModelForm):
    class Meta:
        model = UserTeam
        fields = ('name',)
        labels = {'name': 'Ще го кръстя...'}
        widgets = {
            'name': forms.TextInput(attrs={'placeholder': 'Отбор Бахур'}),
        }

    def clean_name(self):
        name = self.cleaned_data['name']
        slug = slugify(unidecode.unidecode(name))
        if UserTeam.objects.filter(slug=slug).exists():
            raise forms.ValidationError('Тоя тим някой вече го е създал. Пробвай някое друго име.')
        return name
