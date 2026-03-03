from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm, PasswordChangeForm, PasswordResetForm, UserChangeForm
from ECommerceSite.utils import trimite_mail_admin_custom


class UserAuthForm(AuthenticationForm):
    class Meta:
        model = get_user_model()
        widgets = {
            'username': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Username',
            }),
            'password': forms.PasswordInput(attrs={
                "autocomplete": "current-password",
                'class': 'form-control',
            })
        }
class UserRegisterForm(UserCreationForm):

    def clean_username(self):
        username = self.cleaned_data.get('username')
        email = self.cleaned_data.get('email')
        if username and username.lower() == 'admin':

            msg = f"Tentativa de inregistrare cu username 'admin'. Email folosit: {email}"

            trimite_mail_admin_custom(
                subiect="cineva incearca sa ne furee site-ul",
                mesaj_text=msg
            )
            raise forms.ValidationError("Acest username nu este permis.")

        return username
    class Meta:
        model = get_user_model()
        fields = ['username', 'email', 'password1', 'password2']
class UserUpdateForm(UserChangeForm):
    class Meta:
        model = get_user_model()
        fields = ['name', 'username', 'email','phone_number','date_of_birth']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Name',
                'autocomplete': 'current-name',
            }),
            'username': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Username',
                'autocomplete': 'current-user',
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'Email',
                'autocomplete': 'current-email',
            }),
            'phone_number': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Phone Number',
                'autocomplete': 'current-phone',
            }),
            'date_of_birth': forms.DateInput(attrs={
                'class': 'form-control',
                'placeholder': 'Date of Birth',
                'autocomplete': 'current-date',
            })


        }
