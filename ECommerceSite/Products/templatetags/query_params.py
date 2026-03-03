from django import template
import re

register = template.Library()


@register.filter
def remove_page_param(query_dict_string):
    """
    Elimină parametrul 'page' dintr-un string de query parameters.
    Exemplu: "sort=price&page=2" -> "sort=price"
    """
    if not query_dict_string:
        return ""

    # Elimină '&page=123' sau 'page=123'
    return re.sub(r'&?page=\d+', '', query_dict_string)