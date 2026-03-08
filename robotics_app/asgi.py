"""ASGI config for the robotics control project.

This module contains the ASGI application used for asynchronous
deployments. It exposes a module-level variable named ``application``.
"""

import os
from django.core.asgi import get_asgi_application  # type: ignore

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'robotics_app.settings')

application = get_asgi_application()
