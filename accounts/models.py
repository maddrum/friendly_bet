from django.db import models
from django.contrib.auth import get_user_model


class UserExtendModel(models.Model):
    user = models.OneToOneField(get_user_model(), on_delete=models.CASCADE, related_name='extra')

    def get_user_names(self):
        if self.user.first_name or self.user.last_name:
            return f'{self.user.first_name} {self.user.last_name}'
        return f'{self.user.username}'


class LastUserMatchInputStart(models.Model):
    user = models.OneToOneField(get_user_model(), on_delete=models.CASCADE, related_name='user_last_input_start')
    started_on = models.DateTimeField(auto_now=True)
    valid_to = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return self.user.username
