from django.contrib import admin

from mensajes.models import GlobalMessage, UserMessage

admin.site.register(GlobalMessage)
admin.site.register(UserMessage)