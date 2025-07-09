from django import template

register = template.Library()

@register.filter
def filter_status(applications, status):
    return [app for app in applications if app.status == status] 