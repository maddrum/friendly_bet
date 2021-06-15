import datetime

from django import template
from django.utils import timezone

from bonus_points.settings import LAST_BONUS_VISIT_TIME_KEY

register = template.Library()
from bonus_points.models import BonusDescription


@register.simple_tag(takes_context=True)
def check_for_new_bonuses(context):
    now_minus_days = timezone.now() - datetime.timedelta(days=3)
    bonus_check = BonusDescription.objects.filter(created_on__gte=now_minus_days, bonus_active=True).order_by(
        '-created_on')
    if bonus_check.exists():
        if LAST_BONUS_VISIT_TIME_KEY in context.request.session:
            last_time_visit = datetime.datetime.fromisoformat(context.request.session[LAST_BONUS_VISIT_TIME_KEY])
            if bonus_check.first().created_on < last_time_visit:
                return False
    return bonus_check.exists()
