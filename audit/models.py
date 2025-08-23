from django.db import models

from usuarios.models import User


class AuditLog(models.Model):
    class AuditTypes(models.TextChoices):
        AUTH = 'Auth',
        CREATE = 'Create',
        UPDATE = 'Update',
        DELETE = 'Delete',
        FAIL = 'Fail',
        URGENT = 'Urgent',

    user = models.ForeignKey(User, on_delete=models.PROTECT)
    audit_type = models.CharField(max_length=50, choices=AuditTypes.choices, null=True)
    description = models.TextField(null=True)
    ip_address = models.GenericIPAddressField(null=True)
    user_agent = models.TextField(null=True)
    created_at = models.DateTimeField(auto_now_add=True)
