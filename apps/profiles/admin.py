from django.contrib import admin

from .models import Profile


class ProfileAdmin(admin.ModelAdmin):
    """"""

    list_display = (
        "user",
        # "nickname",
        # "phone",
        # "location",
    )
    list_filter = ("user",)
    search_fields = (
        "user",
        "nickname",
        "phone",
    )
    ordering = ("-created_date",)

    def get_inline_instances(self, request, obj=None):
        if not obj:
            return list()
        return super(ProfileAdmin, self).get_inline_instances(request, obj)


admin.site.register(Profile, ProfileAdmin)
