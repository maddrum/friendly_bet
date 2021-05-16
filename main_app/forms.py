from django import forms
from main_app.models import SiteContact


class ContactForm(forms.ModelForm):
    class Meta:
        model = SiteContact
        fields = ('name', 'email', 'message')
        labels = {
            'name': 'Кой си ти?',
            'email': 'email за контакт',
            'message': 'Какво ще питаш?',
        }
        widgets = {
            'message': forms.Textarea(),
        }
