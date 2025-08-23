from django import template

from audit.models import AuditLog
register = template.Library()

TYPE_COLORS = {
    AuditLog.AuditTypes.AUTH: 'is-link',
    AuditLog.AuditTypes.CREATE: 'is-success',
    AuditLog.AuditTypes.UPDATE: 'is-info',
    AuditLog.AuditTypes.DELETE: 'is-warning',
    AuditLog.AuditTypes.FAIL: 'is-text',
    AuditLog.AuditTypes.URGENT: 'is-danger',

}

@register.filter
def audit_color(value):
    return TYPE_COLORS.get(value, 'is-text')

