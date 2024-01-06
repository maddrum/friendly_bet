from django.contrib.auth import get_user_model
from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    def __str__(self):
        return f"{self.username}"

    def get_user_names(self):
        if self.first_name or self.last_name:
            return f"{self.first_name} {self.last_name}"
        return f"{self.username}"


class LastUserMatchInputStart(models.Model):
    user = models.OneToOneField(
        get_user_model(), on_delete=models.CASCADE, related_name="user_last_input_start"
    )
    started_on = models.DateTimeField(auto_now=True)
    valid_to = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return self.user.username
