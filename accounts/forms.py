import re
from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import authenticate
from django.core.exceptions import ValidationError
from .models import User, UserProfile
from recipes.models import validate_image_file

class StyledAuthenticationForm(AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({
                'class': 'w-full px-4 py-2.5 rounded-xl border border-stone-300 focus:border-primary-600 focus:ring-2 focus:ring-primary-100 outline-none transition duration-200 text-stone-800 bg-surface-50'
            })

    def clean(self):
        username = self.cleaned_data.get('username')
        password = self.cleaned_data.get('password')

        if username is not None and password:
            # Periksa apakah user ada dan password benar terlepas dari is_active
            user_match = User.objects.filter(username__iexact=username).first()
            if user_match and user_match.check_password(password) and not user_match.is_active:
                raise ValidationError(
                    "Akun Anda dinonaktifkan oleh administrator.",
                    code='inactive',
                )

            self.user_cache = authenticate(self.request, username=username, password=password)
            if self.user_cache is None:
                raise self.get_invalid_login_error()
            else:
                self.confirm_login_allowed(self.user_cache)

        return self.cleaned_data


class RegisterForm(UserCreationForm):
    email = forms.EmailField(required=True, widget=forms.EmailInput(attrs={
        'class': 'w-full px-4 py-2.5 rounded-xl border border-stone-300 focus:border-primary-600 focus:ring-2 focus:ring-primary-100 outline-none transition duration-200 text-stone-800 bg-surface-50',
        'placeholder': 'nama@email.com'
    }))
    display_name = forms.CharField(max_length=100, required=False, widget=forms.TextInput(attrs={
        'class': 'w-full px-4 py-2.5 rounded-xl border border-stone-300 focus:border-primary-600 focus:ring-2 focus:ring-primary-100 outline-none transition duration-200 text-stone-800 bg-surface-50',
        'placeholder': 'Nama Koki / Panggilan'
    }))

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ('username', 'email')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].widget.attrs.update({
            'class': 'w-full px-4 py-2.5 rounded-xl border border-stone-300 focus:border-primary-600 focus:ring-2 focus:ring-primary-100 outline-none transition duration-200 text-stone-800 bg-surface-50',
            'placeholder': 'username_anda'
        })
        if 'password1' in self.fields:
            self.fields['password1'].widget.attrs.update({
                'class': 'w-full px-4 py-2.5 rounded-xl border border-stone-300 focus:border-primary-600 focus:ring-2 focus:ring-primary-100 outline-none transition duration-200 text-stone-800 bg-surface-50'
            })
        if 'password2' in self.fields:
            self.fields['password2'].widget.attrs.update({
                'class': 'w-full px-4 py-2.5 rounded-xl border border-stone-300 focus:border-primary-600 focus:ring-2 focus:ring-primary-100 outline-none transition duration-200 text-stone-800 bg-surface-50'
            })

    def clean_email(self):
        email = self.cleaned_data.get('email', '').strip().lower()
        if User.objects.filter(email__iexact=email).exists():
            raise ValidationError("Alamat email ini sudah terdaftar. Silakan gunakan email lain.")
        return email

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data.get('email', '').lower()
        if commit:
            user.save()
            display_name = self.cleaned_data.get('display_name') or user.username
            profile, created = UserProfile.objects.get_or_create(user=user)
            profile.display_name = display_name
            profile.save()
        return user


class ProfileUpdateForm(forms.ModelForm):
    display_name = forms.CharField(max_length=100, required=False, widget=forms.TextInput(attrs={
        'class': 'w-full px-4 py-2.5 rounded-xl border border-stone-300 focus:border-primary-600 focus:ring-2 focus:ring-primary-100 outline-none transition duration-200 text-stone-800 bg-surface-50'
    }))
    bio = forms.CharField(widget=forms.Textarea(attrs={
        'rows': 3,
        'class': 'w-full px-4 py-2.5 rounded-xl border border-stone-300 focus:border-primary-600 focus:ring-2 focus:ring-primary-100 outline-none transition duration-200 text-stone-800 bg-surface-50',
        'placeholder': 'Ceritakan kecintaanmu pada masakan nusantara...'
    }), required=False)

    class Meta:
        model = UserProfile
        fields = ('display_name', 'bio', 'avatar')

    def clean_avatar(self):
        avatar = self.cleaned_data.get('avatar')
        if avatar:
            validate_image_file(avatar)
        return avatar
