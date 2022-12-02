from django import template
from django.db.models import Sum

from predictions.models import PredictionPoint

register = template.Library()

RANKING_BREAKPOINTS = {
    # [html_row_class, image_name, image_width, image_class, row_wrapper]
    1: ['rankings1', 'Rank1.png', 431, 'first', ''],
    2: ['rankings1', 'Rank2.png', 200, 'third', 'second-txt'],
    3: ['rankings1', 'Rank3.png', 200, 'third', 'third-txt'],
    4: ['rankings2', 'Rank4.png', 200, 'napadatel', 'napadatel-txt'],
    8: ['rankings3', 'Rank5.png', 150, 'half', 'napadatel-txt'],
    12: ['rankings4', 'Rank6.png', 120, 'bek', 'napadatel-txt'],
    16: ['rankings5', 'Rank7.png', 100, 'bojinka', 'napadatel-txt'],
}

BREAKPOINT_KEYS = [item for item in RANKING_BREAKPOINTS.keys()]
BREAKPOINT_KEYS.sort()
MAX_KEY = max(BREAKPOINT_KEYS)


def get_breakpoint_value(check_value):
    if check_value > MAX_KEY:
        return RANKING_BREAKPOINTS[MAX_KEY]
    if check_value in BREAKPOINT_KEYS:
        return RANKING_BREAKPOINTS[check_value]
    lower_value = [item for item in BREAKPOINT_KEYS if item < check_value][-1]
    return RANKING_BREAKPOINTS[lower_value]


@register.simple_tag
def get_rank_html_class(forloop_counter):
    return get_breakpoint_value(forloop_counter)[0]


@register.simple_tag
def get_rank_image_name(forloop_counter):
    return get_breakpoint_value(forloop_counter)[1]


@register.simple_tag
def get_rank_image_width(forloop_counter):
    return get_breakpoint_value(forloop_counter)[2]


@register.simple_tag
def get_rank_image_class(forloop_counter):
    return get_breakpoint_value(forloop_counter)[3]


@register.simple_tag
def get_row_wrapper(forloop_counter):
    return get_breakpoint_value(forloop_counter)[4]


@register.simple_tag
def gin_is_happy():
    return PredictionPoint.objects.all().aggregate(Sum('additional_points')).get('additional_points__sum') * -1 > 0
