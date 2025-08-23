from django import template

from gestor.models import Petition, Item, Type

register = template.Library()

PETITIONSTATUS_ICONS = {
    Petition.Status.DECLINED: 'iconoir-xmark',
    Petition.Status.PENDING: 'iconoir-hourglass',
    Petition.Status.ACTIVE: 'iconoir-play-solid',
    Petition.Status.EXPIRED: 'iconoir-clock-rotate-right',
    Petition.Status.COLLECTED: 'iconoir-bag'
}

ITEMSTATUS_ICONS = {
    Item.Status.AVAILABLE: 'iconoir-clipboard-check',
    Item.Status.IN_USE: 'iconoir-refresh',
    Item.Status.BLOCKED: 'iconoir-lock'
}

TYPESTATUS_ICONS = {
    Type.Status.AVAILABLE: 'iconoir-clipboard-check',
    Type.Status.BLOCKED: 'iconoir-lock'
}

@register.filter
def petitionstatus_icon(status):
    return PETITIONSTATUS_ICONS.get(status, 'iconoir-emoji-bug')

@register.filter
def itemstatus_icon(status):
    return ITEMSTATUS_ICONS.get(status, 'iconoir-emoji-bug')

@register.filter
def typestatus_icon(status):
    return TYPESTATUS_ICONS.get(status, 'iconoir-emoji-bug')