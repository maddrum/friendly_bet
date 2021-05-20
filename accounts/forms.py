from captcha.fields import ReCaptchaField
from captcha.widgets import ReCaptchaV2Checkbox
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm


class AccountRegisterForm(UserCreationForm):
    captcha = ReCaptchaField(widget=ReCaptchaV2Checkbox())

    class Meta:
        model = get_user_model()
        fields = ('username', 'password1', 'password2')
