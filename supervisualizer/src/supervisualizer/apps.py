# This is the class Django looks up when someone writes INSTALLED_APPS = ["supervisualizer"]

from django.apps import AppConfig

class SupervisualizerConfig(AppConfig):
    name = 'supervisualizer'
    label = 'supervisualizer'
    verbose_name = 'Supervisualizer'
    default_auto_field = 'django.db.models.BigAutoField'