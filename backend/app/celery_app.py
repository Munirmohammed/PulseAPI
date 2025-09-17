from celery import Celery
from .core.config import get_settings


settings = get_settings()

celery = Celery(
    "pulseapi",
    broker=settings.broker(),
    backend=settings.backend(),
)

celery.conf.beat_schedule = {}


