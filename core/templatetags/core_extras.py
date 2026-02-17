from django import template

register = template.Library()


@register.filter
def get_item(mapping, key):
    """
    Safely get a key from a dict-like object in templates.

    Usage:
      {{ my_dict|get_item:"price" }}
    """
    if not mapping:
        return ""
    try:
        return mapping.get(key, "")
    except AttributeError:
        return ""


@register.filter
def form_field(form, field_name):
    """
    Return a BoundField from a Django form using a dynamic field name.

    Usage:
      {% with bf=form|form_field:sf.name %}
        {{ bf }}
        {% if bf.errors %}...{% endif %}
      {% endwith %}
    """
    if not form or not field_name:
        return ""
    try:
        return form[field_name]
    except Exception:
        return ""

