from django.apps import AppConfig


class AgricoleConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'agricole'

    def ready(self):
        from django.apps import apps
        from django.contrib import admin
        try:
            for model_name in ['Materiel', 'ReservationMateriel', 'Alerte']:
                model = apps.get_model('agricole', model_name)
                if not admin.site.is_registered(model):
                    admin.site.register(model)
        except (ImproperlyConfigured, LookupError, ProgrammingError):
            pass