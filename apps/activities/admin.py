from django.contrib import admin

from .models import UserActivity


class UserActivityAdmin(admin.ModelAdmin):
    """"""

    list_display = ("user", "action", "target", "created_date")
    list_filter = "created_date"
    search_fields = ("user", "action", "target")
    ordering = ("-created_date",)


admin.site.register(UserActivity)
