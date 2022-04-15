from django.contrib import admin

from apps.classroom_contents.models import *

admin.site.register(Classwork)
admin.site.register(Resource)
admin.site.register(Submission)
admin.site.register(Attachment)
admin.site.register(ClassworkHasAttachment)
admin.site.register(ClassworkHasSubmission)
admin.site.register(ResourceHasAttachment)
admin.site.register(SubmissionHasAttachment)
