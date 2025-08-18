from django.contrib import admin
from django.contrib.admin import ModelAdmin

from configuracion.models import Configuration

admin.site.register(Configuration, ModelAdmin)