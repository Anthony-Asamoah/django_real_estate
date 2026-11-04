from django.apps import AppConfig


class HelpConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'domains.help'
    label = 'manual'  # 'help' is too easy to collide with
