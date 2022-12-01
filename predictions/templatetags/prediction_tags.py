from django import template

from predictions.models import UserPrediction
from predictions.views_mixins import GetEventMatchesMixin

register = template.Library()


@register.simple_tag(takes_context=True)
def check_prediction_warning(context):
    if context.request.user.is_anonymous:
        return False
    mixin = GetEventMatchesMixin()
    if not mixin.matches.exists():
        return False
    if UserPrediction.objects.filter(user=context.request.user, match__in=mixin.matches).exists():
        return False
    return True
