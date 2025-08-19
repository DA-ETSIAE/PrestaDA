from django import template

from gestor.models import Petition, Item

register = template.Library()

PETITIONSTATUS_COLORS = {
    Petition.PetitionStatus.DECLINED: 'is-danger',
    Petition.PetitionStatus.PENDING: 'is-warning',
    Petition.PetitionStatus.ACTIVE: 'is-success',
    Petition.PetitionStatus.EXPIRED: 'is-link',
    Petition.PetitionStatus.COLLECTED: 'is-text'
}


ITEMSTATUS_COLORS = {
    Item.ItemStatus.AVAILABLE: 'is-primary',
    Item.ItemStatus.IN_USE: 'is-text',
    Item.ItemStatus.BLOCKED: 'is-danger'
}

@register.filter
def petitionstatus_color(value):
    return PETITIONSTATUS_COLORS.get(value, 'is-text')

@register.filter
def itemstatus_color(value):
    return ITEMSTATUS_COLORS.get(value, 'is-text')