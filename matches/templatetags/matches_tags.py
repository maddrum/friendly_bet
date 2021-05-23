from django import template

register = template.Library()


@register.simple_tag
def get_match_home_result(match_result):
    if match_result.penalties:
        return match_result.score_after_penalties_home
    return match_result.score_home


@register.simple_tag
def get_match_guest_result(match_result):
    if match_result.penalties:
        return match_result.score_after_penalties_guest
    return match_result.score_guest
