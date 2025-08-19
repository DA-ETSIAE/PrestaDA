from django.db import models

from usuarios.models import User
from django.utils.translation import gettext_lazy as _

class UserMessage(models.Model):
    user = models.ForeignKey(User, on_delete=models.PROTECT)
    content = models.TextField()
    is_read = models.BooleanField(default=False)
    is_from_staff = models.BooleanField(default=False)
    date_created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.date_created.strftime("%d/%m/%Y") + " / " + self.user.first_name + " " + self.user.last_name

class GlobalMessage(models.Model):
    class Colors(models.TextChoices):
        BLACK = 'text', _('Black')
        BLUE = 'link', _('Blue')
        GREEN_BLUE = 'primary', _('Greenish Blue')
        LIGHT_BLUE = 'info', _('Light Blue')
        GREEN = 'success', _('Green')
        YELLOW = 'warning', _('Yellow')
        RED = 'danger', _('Red')

    title = models.CharField(max_length=100, blank=True, null=True)
    content = models.TextField(blank=False)
    is_active = models.BooleanField(default=True)
    color = models.CharField(max_length=20, choices=Colors.choices, default=Colors.GREEN)
    date_created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        if self.title:
            return self.title
        else:
            return self.date_created.strftime("%d/%m/%Y")

