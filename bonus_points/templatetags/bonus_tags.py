import datetime

from django import template
from django.utils import timezone

register = template.Library()
from bonus_points.models import BonusDescription


@register.simple_tag
def check_for_new_bonuses():
    now_minus_days = timezone.now() - datetime.timedelta(days=2)
    bonus_check = BonusDescription.objects.filter(created_on__gte=now_minus_days, bonus_active=True).exists()
    return bonus_check
