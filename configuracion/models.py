from django.db import models
from django.forms import ModelForm


class Configuration(models.Model):
    node = models.CharField(max_length=100, unique=True)
    value = models.CharField(max_length=100)
    description = models.TextField()
    is_bool = models.BooleanField(default=False)

    def __str__(self):
        return self.node


class ConfigForm(ModelForm):
    class Meta:
        model = Configuration
        fields = ['value']

