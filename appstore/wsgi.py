"""
WSGI config for appstore project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/dev/howto/deployment/wsgi/
"""

import os

from django.core.wsgi import get_wsgi_application

# dev
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "appstore.settings")

# production
#os.environ.setdefault("DJANGO_SETTINGS_MODULE", "appstore.settings_prod")

application = get_wsgi_application()
