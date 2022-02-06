from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import Group
from django.contrib.contenttypes.models import ContentType
from rest_framework_simplejwt import token_blacklist

from .forms import UserAdminChangeForm, UserAdminCreationForm
from .models import CustomUser


# DRF-SIMPLEJWT has a bug where token cannot be deleted by admin. so fix by changing permissions
class OutstandingTokenAdmin(token_blacklist.admin.OutstandingTokenAdmin):
    def has_delete_permission(self, *args, **kwargs):
        return True  # or whatever logic you want


class CustomUserAdmin(BaseUserAdmin):
    form = UserAdminChangeForm
    add_form = UserAdminCreationForm

    list_display = (
        "email",
        "username",
        "registered_date",
    )
    list_filter = ("staff", "active", "admin", "email_verified")
    fieldsets = (
        ("Required", {"fields": ("username", "email", "password")}),
        ("Permissions", {"fields": ("admin", "staff", "active")}),
        ("Verifications", {"fields": ("email_verified",)}),
    )
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": ("username", "email", "password1", "password2"),
            },
        ),
    )

    search_fields = ("email", "username")
    ordering = ("registered_date",)
    filter_horizontal = ()

    def get_inline_instances(self, request, obj=None):
        if not obj:
            return list()
        return super(CustomUserAdmin, self).get_inline_instances(request, obj)


admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(ContentType)
admin.site.unregister(Group)
admin.site.unregister(token_blacklist.models.OutstandingToken)
admin.site.register(token_blacklist.models.OutstandingToken, OutstandingTokenAdmin)
