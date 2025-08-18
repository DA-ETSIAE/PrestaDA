from django.contrib import admin
from django.contrib.admin import ModelAdmin
from django.contrib.auth.admin import UserAdmin

from usuarios.models import User

admin.site.register(User, ModelAdmin)