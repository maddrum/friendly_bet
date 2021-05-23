from django.db import models
from django.contrib.auth import get_user_model
from django.db.models.signals import post_save


class UserExtendModel(models.Model):
    user = models.OneToOneField(get_user_model(), on_delete=models.CASCADE, related_name='extra')

    def __str__(self):
        return f'{self.user}'

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


def user_post_save(sender, instance, created, *args, **kwargs):
    extra_obj, created = UserExtendModel.objects.get_or_create(user=instance)
    extra_obj.save()


post_save.connect(user_post_save, get_user_model())
