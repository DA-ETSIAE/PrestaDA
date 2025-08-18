from django.db import models

from usuarios.models import User


class UserMessage(models.Model):
    user = models.ForeignKey(User, on_delete=models.PROTECT)
    content = models.TextField()
    is_read = models.BooleanField(default=False)
    is_from_staff = models.BooleanField(default=False)
    date_created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.date_created.strftime("%d/%m/%Y") + " / " + self.user.first_name + " " + self.user.last_name

class GlobalMessage(models.Model):
    has_title = models.BooleanField(default=True)
    title = models.CharField(max_length=100, blank=True, null=True)
    content = models.TextField(blank=False)
    is_active = models.BooleanField(default=True)
    color = models.CharField(max_length=30, default="primary")
    date_created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        if self.has_title:
            return self.title
        else:
            return self.date_created.strftime("%d/%m/%Y")