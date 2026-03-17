"""Gunicorn/Render compatibility module.

This allows startup commands like `gunicorn app` or `gunicorn app:app`
to boot the Django WSGI application.
"""

from organ_donation.wsgi import application

# Common alias used by some default PaaS gunicorn commands.
app = application
