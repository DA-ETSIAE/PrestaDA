from django.db import models

from usuarios.models import User


class AuditLog(models.Model):
    AUDIT_CHOICES = [
        ('AUTH', 'Auth'),
        ('LOGOUT', 'Logout'),
        ('UPDATE', 'Update'),
        ('CREATE', 'Create'),
        ('DELETE', 'Delete'),
        ('URGENT', 'Urgent'),
    ]

    user = models.ForeignKey(User, on_delete=models.PROTECT)
    audit_type = models.CharField(max_length=50, choices=AUDIT_CHOICES, null=True)
    description = models.TextField(null=True)
    ip_address = models.GenericIPAddressField(null=True)
    user_agent = models.TextField(null=True)
    created_at = models.DateTimeField(auto_now_add=True)
