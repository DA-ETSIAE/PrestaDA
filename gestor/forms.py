from django import forms
from django.forms.models import ModelForm

from gestor.models import Petition, Item, Type


class SavePetitionForm(ModelForm):
    class Meta:
        model = Petition
        fields = ['until', 'item']


class ValidateForm(forms.Form):
    dni = forms.CharField(max_length=20)
    pid = forms.IntegerField()
    hashed = forms.CharField(widget=forms.Textarea)


class SaveTypeForm(ModelForm):
    class Meta:
        model = Type
        fields = ['name', 'conditions', 'description', 'is_blocked']

class SaveItemForm(ModelForm):
    class Meta:
        model = Item
        fields = ['code', 'type', 'notes', 'status']
