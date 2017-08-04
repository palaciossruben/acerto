from django.contrib.auth import forms as auth_forms


def validate_password_strength(value):
    """
    Passwords can be anything.
    Args:
        value: Raw password.
    Returns: identity function, there is NO validation
    """
    return value


class AdminPasswordChangeForm(auth_forms.AdminPasswordChangeForm):

    def clean_password1(self):
        return validate_password_strength(self.cleaned_data['password1'])

    def clean_password2(self):
        return validate_password_strength(self.cleaned_data['password2'])


class CustomUserCreationForm(auth_forms.UserCreationForm):
    """ This class is created to override password verification and make it easier to register.
    """

    def clean_password1(self):
        return validate_password_strength(self.cleaned_data['password1'])

    def clean_password2(self):
        return validate_password_strength(self.cleaned_data['password2'])
