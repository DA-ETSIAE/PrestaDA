from django.contrib.auth import user_logged_in
from django.dispatch import receiver

from audit.models import AuditLog
from audit.utils import create_audit


@receiver(user_logged_in)
def handle_user_logged_in(sender, request, user, **kwargs):
    create_audit(request, AuditLog.AuditTypes.AUTH, 'Logged-in')