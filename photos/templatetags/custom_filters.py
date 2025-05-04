from django import template
import json

register = template.Library()


@register.filter(name="parse_json")
def parse_json(value):
    try:
        return json.loads(value).items()
    except (ValueError, TypeError):
        return {}
