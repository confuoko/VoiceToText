import os
from celery import Celery


os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'user_account.settings')

app = Celery('sendmail')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks() # таски подцепляются автоматически
