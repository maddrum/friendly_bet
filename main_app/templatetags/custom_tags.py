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
