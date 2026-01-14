"""
WSGI config for presentation_project project.
"""

import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'presentation_project.settings')

application = get_wsgi_application()
