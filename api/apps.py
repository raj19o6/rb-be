from django.apps import AppConfig


class ApiConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'api'

    def ready(self):
        import api.User.model
        import api.UserProfile.model
        import api.HierarchyPermission.model
        import api.CustomRole.model
