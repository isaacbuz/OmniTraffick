"""Celery application configuration."""
from celery import Celery
from src.config import settings

celery_app = Celery(
    "omnitraffick",
    broker=settings.celery_broker_url,
    backend=settings.celery_result_backend,
    include=["src.workers.tasks"],
)

# Celery configuration
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=300,  # 5 minutes
    task_soft_time_limit=240,  # 4 minutes
    worker_prefetch_multiplier=1,
    task_acks_late=True,
    task_reject_on_worker_lost=True,
)

# Retry configuration
celery_app.conf.task_default_retry_delay = 30  # 30 seconds
celery_app.conf.task_max_retries = 3
