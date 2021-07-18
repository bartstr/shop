from .models import Product
from django import forms
from django.contrib.auth.models import User


class LoginForm(forms.Form):
    username = forms.CharField(max_length=100, label='Login')
    password = forms.CharField(widget=forms.PasswordInput(), label='Hasło')

    def clean_username(self):
        username = self.cleaned_data['username']
        try:
            User.objects.get(username=username)
        except User.DoesNotExist:
            raise forms.ValidationError('Username does not exist.')


class AddProduct(forms.ModelForm):
    name = forms.CharField(label='Nazwa')
    producer = forms.CharField(label='Producent')
    description = forms.CharField(widget=forms.Textarea(), label='Opis')
    price = forms.FloatField(label='Cena')
    image = forms.ImageField(widget=forms.FileInput(), label='Dodaj zdjęcie')

    class Meta:
        model = Product
        fields = ('name', 'producer', 'description', 'price', 'image')


class Search(forms.Form):
    phrase = forms.CharField(label='Szukaj')
