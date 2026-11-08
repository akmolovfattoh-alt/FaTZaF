from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Profile, Message
from django.core.exceptions import ValidationError


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
        fields = ('body', 'attachment')

        widgets = {
            'body': forms.Textarea(attrs={
                'rows': 1,
                'placeholder': 'Напишите сообщение…'
            })
        }

    def clean_attachment(self):
        file = self.cleaned_data.get('attachment')

        if file:
            if file.size > 25 * 1024 * 1024:
                raise ValidationError(
                    'Максимальный размер файла — 25 МБ.'
                )

        return file

    def clean(self):
        cleaned_data = super().clean()

        body = cleaned_data.get('body')
        attachment = cleaned_data.get('attachment')

        if not body and not attachment:
            raise ValidationError(
                'Напишите сообщение или прикрепите файл.'
            )
        return cleaned_data