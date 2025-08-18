from django.db import models

from usuarios.models import User


class Type(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True, null=True)
    conditions = models.TextField(blank=True, null=True)
    is_blocked = models.BooleanField(default=False)

    def __str__(self):
        return self.name


class Item(models.Model):
    code = models.CharField(max_length=50)
    type = models.ForeignKey(Type, on_delete=models.PROTECT)
    notes = models.CharField(max_length=200, blank=True, null=True)
    is_available = models.BooleanField(default=True)
    is_blocked = models.BooleanField(default=False)

    def __str__(self):
        return self.code

class Petition(models.Model):
    type = models.ForeignKey(Type, on_delete=models.PROTECT)
    item = models.ForeignKey(Item, on_delete=models.PROTECT, null=True, blank=True)
    user = models.ForeignKey(User, on_delete=models.PROTECT)
    date = models.DateTimeField(auto_now_add=True)
    date_reserved = models.DateTimeField(null=True, blank=True)
    until = models.DateTimeField(null=True, blank=False)
    is_pending = models.BooleanField(default=True)
    is_active = models.BooleanField(default=False)

    def __str__(self):
        return str(self.id)


