from django.contrib import admin

from apps.class_groups.models import (
    ClassGroup,
    ClassGroupHasClassroom,
    ClassGroupHasRoutineSchedules,
    ClassGroupHasStudent,
    ClassGroupStudentInviteOrRequest,
)


class IDExtendAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "name",
    )


class ClassGroupHasStudentAdmin(admin.ModelAdmin):
    list_display = (
        "classgroup",
        "student",
    )


admin.site.register(ClassGroup, IDExtendAdmin)
admin.site.register(ClassGroupStudentInviteOrRequest)
admin.site.register(ClassGroupHasClassroom)
admin.site.register(ClassGroupHasStudent, ClassGroupHasStudentAdmin)
admin.site.register(ClassGroupHasRoutineSchedules)
