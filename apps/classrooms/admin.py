from django.contrib import admin

from apps.classrooms.models import *

admin.site.register(Classroom)
admin.site.register(ClassroomHasStudent)
admin.site.register(ClassroomHasTeacher)
admin.site.register(ClassroomHasClasswork)
admin.site.register(ClassroomHasResource)
admin.site.register(ClassroomInviteOrRequest)
admin.site.register(ClassroomHasSchedule)
