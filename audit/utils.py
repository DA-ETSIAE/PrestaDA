from typing import Optional

from audit.models import AuditLog


def create_audit(request, audit_type: str, description: Optional[str] = None):
    audit = AuditLog()
    audit.user = request.user
    audit.audit_type = audit_type
    audit.description = description
    audit.ip_address = request.META.get('HTTP_X_FORWARDED_FOR')
    audit.user_agent = request.META.get('HTTP_USER_AGENT')
    audit.save()