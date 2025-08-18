from django.db import models

from django.contrib.auth.models import AbstractUser
from django.forms.models import ModelForm

class User(AbstractUser):
    is_logged_by_sso = models.BooleanField(default=False)

    dni = models.CharField(max_length=20, blank=False, null=True)
    phone = models.CharField(max_length=11, null=True, blank=False)

    max_petitions = models.PositiveIntegerField(default=5)
    max_items = models.PositiveIntegerField(default=5)

    is_banned = models.BooleanField(default=False)
    banned_reason = models.TextField(blank=False, null=True)
    banned_at = models.DateTimeField(null=True, blank=True)

    can_bypass_maint = models.BooleanField(default=False)

    is_local_user = models.BooleanField(default=False)

    is_new_user = models.BooleanField(default=True)

    def staff_check(self):
        return self.is_staff

    def superuser_check(self):
        return self.is_superuser


class SetupForm(ModelForm):
    class Meta:
        model = User
        fields = ['dni', 'phone']


class BanForm(ModelForm):
    class Meta:
        model = User
        fields = ['banned_reason']