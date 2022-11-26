from django import template

register = template.Library()


@register.filter
def get_list_index_value(input_list, index):
    return input_list[int(index)]


@register.filter
def get_value_from_dict_key(dictionary, key):
    return dictionary.get(key)


@register.simple_tag
def get_values_from_dictionary_tag(dictionary, key):
    return dictionary.get(key)


@register.filter
def absolute_value(value):
    return abs(value)


@register.simple_tag
def replace_str(initial_str, value_to_replace, value_to_replace_with):
    return str(initial_str).replace(value_to_replace, value_to_replace_with)
