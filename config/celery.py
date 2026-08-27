import os
from celery import Celery

# Устанавливаем настройки Django по умолчанию для Celery
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

app = Celery("config")

# Читаем настройки из settings.py
app.config_from_object("django.conf:settings", namespace="CELERY")

# Автоматически ищем tasks.py в приложениях
app.autodiscover_tasks()
