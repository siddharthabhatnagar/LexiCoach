from celery import Celery
from app.core.config import settings
from app.modules import daily_vocab_task, weekly_report_task

celery_app = Celery(
    "english_app",
    broker=settings.celery_broker_url,
    backend=settings.celery_result_backend,
)
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    beat_schedule={
        "daily_vocab_generation": {
            "task": "app.modules.daily_vocab_task.generate_daily_vocab_for_users",
            "schedule": 86400.0,
        },
        "weekly_report_generation": {
            "task": "app.modules.weekly_report_task.generate_weekly_reports",
            "schedule": 604800.0,
        },
    },
)
