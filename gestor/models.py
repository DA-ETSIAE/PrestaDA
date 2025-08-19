from django.db import models
from django.utils.translation import gettext_lazy as _

from usuarios.models import User


class Type(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True, null=True)
    conditions = models.TextField(blank=True, null=True)
    is_blocked = models.BooleanField(default=False)

    def __str__(self):
        return self.name


class Item(models.Model):
    class ItemStatus(models.TextChoices):
        AVAILABLE = "available", _('Available')
        BLOCKED = "blocked", _('Blocked')
        IN_USE = "in_use", _('In Use')

    code = models.CharField(max_length=50)
    type = models.ForeignKey(Type, on_delete=models.PROTECT)
    notes = models.CharField(max_length=200, blank=True, null=True)
    status = models.CharField(max_length=40, choices=ItemStatus.choices, default=ItemStatus.AVAILABLE)

    def __str__(self):
        return self.code

class Petition(models.Model):
    class PetitionStatus(models.TextChoices):
        DECLINED = 'DECLINED', _('Declined')
        PENDING = 'PENDING', _('Pending')
        ACTIVE = 'ACTIVE', _('Active')
        EXPIRED = 'EXPIRED', _('Expired')
        COLLECTED = 'COLLECTED', _('Collected')

    type = models.ForeignKey(Type, on_delete=models.PROTECT)
    item = models.ForeignKey(Item, on_delete=models.PROTECT, null=True, blank=False)
    user = models.ForeignKey(User, on_delete=models.PROTECT)
    date = models.DateTimeField(auto_now_add=True)
    date_reserved = models.DateTimeField(null=True, blank=True)
    until = models.DateTimeField(null=True, blank=False)
    status = models.CharField(max_length=40, choices=PetitionStatus.choices, default=PetitionStatus.PENDING)

    def __str__(self):
        return str(self.id)


