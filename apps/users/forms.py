from django import forms
from django.contrib.auth.forms import ReadOnlyPasswordHashField

from .models import CustomUser


class UserAdminCreationForm(forms.ModelForm):
    password1 = forms.CharField(label="Password", widget=forms.PasswordInput)
    password2 = forms.CharField(label="Confirm Password", widget=forms.PasswordInput)

    class Meta:
        model = CustomUser
        fields = ("email",)

    def clean_password2(self):
        """Checks by comparing password2 with password1 and Returns password2"""

        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")

        if not password1:
            raise forms.ValidationError("Password not found")
        if not password2:
            raise forms.ValidationError("Confirmation Password not found")
        if password1 != password2:
            raise forms.ValidationError(
                "Passwords do not match. Please check passwords and try again"
            )

        return password2

    def save(self, commit: bool = True):
        """Saves the user using super"""

        new_user = super(UserAdminCreationForm, self).save(commit=False)
        new_user.set_password(self.cleaned_data["password1"])
        new_user.save()
        return new_user


class UserAdminChangeForm(forms.ModelForm):

    password = ReadOnlyPasswordHashField()

    class Meta:
        model = CustomUser
        fields = (
            "email",
            "password",
            "active",
            "admin",
            "staff",
            "email_verified",
        )

    def clean_password(self):
        return self.initial["password"]
