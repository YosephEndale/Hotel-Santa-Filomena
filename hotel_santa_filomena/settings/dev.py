from .base import *

DEBUG = True

ALLOWED_HOSTS = ['localhost', '127.0.0.1']

# Emails print to terminal in dev — no real SMTP needed
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'