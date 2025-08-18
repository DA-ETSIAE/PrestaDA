from django.forms import ModelForm

from mensajes.models import GlobalMessage, UserMessage
from usuarios.models import User


class GlobalForm(ModelForm):
    class Meta:
        model = GlobalMessage
        fields = ['title', 'content', 'color']


class UserForm(ModelForm):
    class Meta:
        model = UserMessage
        fields = ['content']
