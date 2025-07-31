from django import template
from MainApp.models import LANG_ICON

register = template.Library()


def get_class_icon(value):
    # {{ lang | get_class_icon }}
    return LANG_ICON.get(value)

def messages_type_mapping(value):
    mapping = {
        "error": "danger",
        "debug": "dark",
    }
    return mapping.get(value, value)


register.filter("get_class_icon", get_class_icon)
register.filter("messages_type_mapping", messages_type_mapping)
