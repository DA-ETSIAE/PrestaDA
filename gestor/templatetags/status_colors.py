from django import template

from gestor.models import Petition, Item, Type

register = template.Library()

PETITIONSTATUS_COLORS = {
    Petition.Status.DECLINED: 'is-danger',
    Petition.Status.PENDING: 'is-warning',
    Petition.Status.ACTIVE: 'is-success',
    Petition.Status.EXPIRED: 'is-link',
    Petition.Status.COLLECTED: 'is-text'
}


ITEMSTATUS_COLORS = {
    Item.Status.AVAILABLE: 'is-primary',
    Item.Status.IN_USE: 'is-text',
    Item.Status.BLOCKED: 'is-danger'
}

TYPESTATUS_COLORS = {
    Type.Status.AVAILABLE: 'is-primary',
    Type.Status.BLOCKED: 'is-danger'

}

@register.filter
def petitionstatus_color(value):
    return PETITIONSTATUS_COLORS.get(value, 'is-text')

@register.filter
def itemstatus_color(value):
    return ITEMSTATUS_COLORS.get(value, 'is-text')

@register.filter
def typestatus_color(value):
    return TYPESTATUS_COLORS.get(value, 'is-text')