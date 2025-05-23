import os
from django.conf import settings
from celery import Celery


os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ChatBox.settings')

app = Celery('ems')
app.conf.broker_url = settings.REDIS_URL
app.config_from_object('django.conf:settings', namespace='CELERY')


@app.task(bind=True)
def debug_task(self):
    print('Request: {self.request!r}')
