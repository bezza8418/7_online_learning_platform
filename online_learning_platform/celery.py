import os
from celery import Celery

# Устанавливаем настройки Django по умолчанию
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'online_learning_platform.settings')

app = Celery('online_learning_platform')

# Загружаем настройки из Django
app.config_from_object('django.conf:settings', namespace='CELERY')

# Принудительно RESP2
app.conf.broker_transport_options = {'protocol': 2}
app.conf.result_backend_transport_options = {'protocol': 2}

# Автоматически находим задачи в приложениях
app.autodiscover_tasks()
