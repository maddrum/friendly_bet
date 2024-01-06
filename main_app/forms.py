from django import forms
from main_app.models import SiteContact
from django_recaptcha.fields import ReCaptchaField
from django_recaptcha.widgets import ReCaptchaV2Checkbox


class ContactForm(forms.ModelForm):
    captcha = ReCaptchaField(widget=ReCaptchaV2Checkbox())

    class Meta:
        model = SiteContact
        fields = ("name", "email", "message")
        labels = {
            "name": "Кой си ти?",
            "email": "email за контакт",
            "message": "Какво ще питаш?",
        }
        widgets = {
            "message": forms.Textarea(attrs={"rows": 0, "cols": 0}),
        }
