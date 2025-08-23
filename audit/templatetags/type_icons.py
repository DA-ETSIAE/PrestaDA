from django import template

from audit.models import AuditLog
register = template.Library()

TYPE_ICONS = {
    AuditLog.AuditTypes.AUTH: 'iconoir-log-in',
    AuditLog.AuditTypes.CREATE: 'iconoir-plus-circle',
    AuditLog.AuditTypes.UPDATE: 'iconoir-refresh-double',
    AuditLog.AuditTypes.DELETE: 'iconoir-emoji-sad',
    AuditLog.AuditTypes.FAIL: 'iconoir-emoji-sad',
    AuditLog.AuditTypes.URGENT: 'iconoir-thunderstorm',

}

@register.filter
def audit_icon(value):
    return TYPE_ICONS.get(value, 'iconoir-emoji-bug')