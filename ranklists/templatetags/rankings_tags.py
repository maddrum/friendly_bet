from django import template
from django.db.models import Sum

from predictions.models import PredictionPoint

register = template.Library()


@register.simple_tag
def gin_is_happy():
    return PredictionPoint.objects.all().aggregate(Sum('additional_points')).get('additional_points__sum') * -1 > 0
