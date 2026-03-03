from django import template

register = template.Library()


@register.filter(name='is_member')
def is_member(user, group_name):

    if hasattr(user, 'is_member'):
        return user.is_member(group_name)

    if user.is_authenticated:
        return user.groups.filter(name=group_name).exists()

    return False