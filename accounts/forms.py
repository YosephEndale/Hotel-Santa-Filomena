from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _


class RegisterForm(UserCreationForm):

    email = forms.EmailField(
        label=_('Email Address'),
        required=True,
        widget=forms.EmailInput(attrs={
            'class':       'auth-form__input',
            'placeholder': _('mario@example.com'),
            'autocomplete': 'email',
        })
    )
    first_name = forms.CharField(
        label=_('First Name'),
        max_length=50,
        widget=forms.TextInput(attrs={
            'class':       'auth-form__input',
            'placeholder': _('Mario'),
            'autocomplete': 'given-name',
        })
    )
    last_name = forms.CharField(
        label=_('Last Name'),
        max_length=50,
        widget=forms.TextInput(attrs={
            'class':       'auth-form__input',
            'placeholder': _('Rossi'),
            'autocomplete': 'family-name',
        })
    )

    class Meta:
        model  = User
        fields = [
            'first_name',
            'last_name',
            'email',
            'username',
            'password1',
            'password2',
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['username'].widget.attrs.update({
            'class':       'auth-form__input',
            'placeholder': _('mariorossi'),
            'autocomplete': 'username',
        })
        self.fields['username'].label = _('Username')
        self.fields['username'].help_text = None

        self.fields['password1'].widget.attrs.update({
            'class':       'auth-form__input',
            'placeholder': '••••••••',
            'autocomplete': 'new-password',
        })
        self.fields['password1'].label    = _('Password')
        self.fields['password1'].help_text = None

        self.fields['password2'].widget.attrs.update({
            'class':       'auth-form__input',
            'placeholder': '••••••••',
            'autocomplete': 'new-password',
        })
        self.fields['password2'].label    = _('Confirm Password')
        self.fields['password2'].help_text = None

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError(
                _('An account with this email already exists.')
            )
        return email

    def save(self, commit=True):
        user            = super().save(commit=False)
        user.email      = self.cleaned_data['email']
        user.first_name = self.cleaned_data['first_name']
        user.last_name  = self.cleaned_data['last_name']
        if commit:
            user.save()
        return user


class LoginForm(AuthenticationForm):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['username'].widget.attrs.update({
            'class':       'auth-form__input',
            'placeholder': _('Username or email'),
            'autocomplete': 'username',
        })
        self.fields['username'].label = _('Username')

        self.fields['password'].widget.attrs.update({
            'class':       'auth-form__input',
            'placeholder': '••••••••',
            'autocomplete': 'current-password',
        })
        self.fields['password'].label = _('Password')