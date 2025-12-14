from django import template

register = template.Library()

@register.filter
def get_status_badge(statut):
    return {
        'en_attente': 'secondary',
        'validee': 'success',
        'annulee': 'danger',
        'en_cours': 'info',
        'expediee': 'primary',
        'livree': 'success',
    }.get(statut, 'secondary')
