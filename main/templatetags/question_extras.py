from django import template

register = template.Library()

@register.filter
def get_option(question, index):
    """
    Возвращает одно из полей option1..option6 по номеру.
    Используется в шаблоне как {{ q|get_option:"1" }}
    """
    return getattr(question, f"option{index}", None)
