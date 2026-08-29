import os
from celery import Celery

# Install Django settings for Celery
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

app = Celery("config")

# Read settings from settings.py
app.config_from_object("django.conf:settings", namespace="CELERY")

# Searching tasks.py in installed apps
app.autodiscover_tasks()
