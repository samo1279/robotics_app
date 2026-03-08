"""Application configuration for the control app.

The ControlConfig class allows Django to perform automatic
configuration of certain behaviours for the app (e.g. signals). It
also names the application so that it can be referenced in settings.
"""
from django.apps import AppConfig


class ControlConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'control'
