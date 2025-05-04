from django import template

register = template.Library()


@register.simple_tag
def pagination_url(page_number, query_params):
    query_params = query_params.copy()
    query_params["page"] = page_number
    return f"?{query_params.urlencode()}"
