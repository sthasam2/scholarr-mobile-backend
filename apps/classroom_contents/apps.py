from django.apps import AppConfig


class ClassroomContentsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.classroom_contents"

    def ready(self):
        import apps.classroom_contents.signals
