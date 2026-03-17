"""Gunicorn/Render compatibility module.

This allows startup commands like ``gunicorn app`` or ``gunicorn app:app``
to boot the Django WSGI application.
"""

import os

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'organ_donation.settings')

# Some Render services are configured with `gunicorn app:app` and bypass `start.sh`.
# Run migrations here as a safety net so dashboard queries don't fail with 500.
from django import setup as django_setup
from django.core.management import call_command

django_setup()
call_command('migrate', interactive=False, run_syncdb=True, verbosity=0)

from organ_donation.wsgi import application

# Common alias used by some default PaaS gunicorn commands.
app = application
