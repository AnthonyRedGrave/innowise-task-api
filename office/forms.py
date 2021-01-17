from django import forms
from .models import *
from django.contrib.auth.models import User
import datetime

class PlaceForm(forms.ModelForm):
    def clean(self):
        data = self.cleaned_data['data']
        now = datetime.date.today()
        if data < now:
            raise forms.ValidationError("Дата для бронирования места некорректна!")
        return self.cleaned_data

    class Meta:
        model = Place
        fields = ['data', 'client', 'occupied']
        widgets = {'client': forms.HiddenInput(),
                   'occupied': forms.HiddenInput()}


class LoginForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)#не будут видны символы

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['username'].label = "Логин пользователя"
        self.fields['password'].label = 'Пароль'

    def clean(self):

        username = self.cleaned_data['username']
        password = self.cleaned_data['password']

        if not User.objects.filter(username = username).exists():
            forms.ValidationError("Пользователь с логином {} не найден".format(username))

        user = User.objects.filter(username = username).first()#первый пользователь с таким логином
        if user:
            if not user.check_password(password):#если пароль не соответствует
                raise forms.ValidationError("Неверный пароль")
        return self.cleaned_data


    class Meta:
        model = User
        fields = ['username', 'password']


class RegisterForm(forms.ModelForm):
    confirm_password = forms.CharField(widget=forms.PasswordInput)
    password = forms.CharField(widget=forms.PasswordInput)
    email = forms.EmailField(required=True)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].label = 'Логин'
        self.fields['password'].label = 'Пароль'
        self.fields['confirm_password'].label = 'Подтверждение пароля'
        self.fields['email'].label = 'Адрес электронной почты'


    def clean_email(self):
        email = self.cleaned_data['email']
        domain_name = email.split('.')[-1]
        if domain_name in ['com', 'net']:
            raise forms.ValidationError("Регистрация с доменом {} невозможна".format(domain_name))
        if User.objects.filter(email = email).exists():
            raise forms.ValidationError("Пользователь с таким адресом эл. почты уже существует")
        return email

    def clean_username(self):
        username = self.cleaned_data['username']
        if User.objects.filter(username = username).exists():# если пользователь с таким именем уже существует
            raise forms.ValidationError("Пользователь с таким логином уже существует")
        return username

    def clean(self):
        password = self.cleaned_data['password']
        confirm_password = self.cleaned_data['confirm_password']

        if password != confirm_password:
            raise forms.ValidationError("Пароли не совпадают")
        return self.cleaned_data

    class Meta:
        model = User
        fields = ['username', 'password', 'confirm_password', 'email']
