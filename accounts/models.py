from django.db import models
from django.contrib.auth import get_user_model


class LastUserMatchInputStart(models.Model):
    user = models.OneToOneField(get_user_model(), on_delete=models.CASCADE, related_name='user_last_input_start')
    started_on = models.DateTimeField(auto_now=True)
    valid_to = models.DateTimeField()
