from django.apps import AppConfig


class ClassGroupsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.class_groups"

    def ready(self):
        import apps.class_groups.signals
