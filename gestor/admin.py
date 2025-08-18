from django.contrib import admin
from django.contrib.admin import ModelAdmin

from gestor.models import Type, Petition, Item

# Register your models here.

admin.site.register(Type)
admin.site.register(Petition)
admin.site.register(Item)