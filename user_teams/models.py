import uuid

import unidecode
from django.contrib.auth import get_user_model
from django.db import models
from django.utils.text import slugify


class UserTeam(models.Model):
    founder = models.ForeignKey(get_user_model(), on_delete=models.CASCADE, related_name='founder')
    name = models.CharField(max_length=50)
    slug = models.SlugField(default='no-slug', unique=True)
    uuid = models.UUIDField(default=uuid.uuid4, primary_key=False, editable=False)
    created_on = models.DateTimeField(auto_now_add=True)
    edited_on = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.name)

    def save(self, *args, **kwargs):
        if self.pk is None:
            self.slug = slugify(unidecode.unidecode(self.name))
        return super(UserTeam, self).save(*args, **kwargs)


class TeamMember(models.Model):
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE, related_name='team_user')
    team = models.ForeignKey(UserTeam, on_delete=models.CASCADE, related_name='team_team')
    approved = models.BooleanField(default=False)
    created_on = models.DateTimeField(auto_now_add=True)
    edited_on = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'{self.team} -> {self.user}: {"Одобрен" if self.approved else "Неодобрен"}'
