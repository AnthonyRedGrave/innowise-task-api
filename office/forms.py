from django import forms
from .models import *
from django.contrib.auth.models import User

class PlaceForm(forms.ModelForm):
    class Meta:
        model = Place
        fields = ['data', 'occupied', 'client']
        widgets = {'client': forms.HiddenInput()}

