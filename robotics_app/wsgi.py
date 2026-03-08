"""WSGI config for the robotics control project.

This module contains the WSGI application used by Django’s development
server and any production WSGI deployments. It exposes a module-level
variable named ``application``. For more information on this file, see
https://docs.djangoproject.com/en/stable/howto/deployment/wsgi/
"""

import os
from django.core.wsgi import get_wsgi_application  # type: ignore


os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'robotics_app.settings')

# The WSGI application callable
application = get_wsgi_application()
