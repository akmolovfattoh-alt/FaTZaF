from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Profile, Message


class RegisterForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')


class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ('bio', 'avatar')


class MessageForm(forms.ModelForm):
    class Meta:
        model = Message
        fields = ('body',)
        widgets = {'body': forms.Textarea(attrs={'rows': 1, 'placeholder': 'Напишите сообщение…'})}
