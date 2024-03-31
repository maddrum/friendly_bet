import typing

from django import template

if typing.TYPE_CHECKING:
    from matches.models import MatchResult

register = template.Library()


@register.simple_tag
def get_match_home_result(match_result: "MatchResult") -> typing.Optional["int"]:
    if not match_result.match_is_over:
        return None
    if match_result.penalties:
        return match_result.score_after_penalties_home
    return match_result.score_home


@register.simple_tag
def get_match_guest_result(match_result: "MatchResult") -> typing.Optional["int"]:
    if not match_result.match_is_over:
        return None
    if match_result.penalties:
        return match_result.score_after_penalties_guest
    return match_result.score_guest
