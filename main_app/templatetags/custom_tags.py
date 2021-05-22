from django import template

# from bonus_points.models import BonusDescription, BonusUserPrediction
# import datetime
#
register = template.Library()


#
#
# @register.simple_tag
# def active_bonuses_checker(logged_user):
#     if logged_user.is_anonymous:
#         return False
#     current_time = datetime.datetime.now()
#     all_bonuses = BonusDescription.objects.filter(active_until__gte=current_time, archived=False,
#                                                   bonus_active=True)
#
#     if all_bonuses.count() == 0:
#         return False
#     for item in all_bonuses:
#         user_participated = BonusUserPrediction.objects.filter(user_bonus_name=item, user=logged_user).count()
#         print(user_participated)
#         if user_participated != 0:
#             continue
#         else:
#             return True
#     return False

@register.filter
def get_list_index_value(input_list, index):
    return input_list[int(index)]


@register.filter
def get_value_from_dict_key(dictionary, key):
    return dictionary.get(key)


@register.simple_tag
def get_values_from_dictionary_tag(dictionary, key):
    return dictionary.get(key)
