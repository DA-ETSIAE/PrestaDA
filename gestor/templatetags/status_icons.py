from django import template

from gestor.models import Petition, Item

register = template.Library()

PETITIONSTATUS_ICONS = {
    Petition.PetitionStatus.DECLINED: 'iconoir-xmark',
    Petition.PetitionStatus.PENDING: 'iconoir-hourglass',
    Petition.PetitionStatus.ACTIVE: 'iconoir-play-solid',
    Petition.PetitionStatus.EXPIRED: 'iconoir-clock-rotate-right',
    Petition.PetitionStatus.COLLECTED: 'iconoir-bag'
}

ITEMSTATUS_ICONS = {
    Item.ItemStatus.AVAILABLE: 'iconoir-clipboard-check',
    Item.ItemStatus.IN_USE: 'iconoir-refresh',
    Item.ItemStatus.BLOCKED: 'iconoir-lock'
}

@register.filter
def petitionstatus_icon(status):
    return PETITIONSTATUS_ICONS.get(status, 'iconoir-emoji-sad')

@register.filter
def itemstatus_icon(status):
    return ITEMSTATUS_ICONS.get(status, 'iconoir-emoji-sad')