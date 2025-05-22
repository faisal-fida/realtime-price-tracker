from celery import Celery
from src.app.core.config import settings

celery_app = Celery(
    "worker",
    broker=str(settings.CELERY_BROKER_URL), # Ensure URL is a string
    backend=str(settings.CELERY_RESULT_BACKEND), # Ensure URL is a string
    include=['src.app.tasks.scraper'] # Explicitly include tasks module
)

# Optional: Update Celery configuration with other settings from your config if needed
celery_app.conf.update(
    task_serializer='json',
    accept_content=['json'],  # Ignore other content
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
)

# Autodiscover tasks from all registered Django app configs.
# For FastAPI, explicit include or this might be adapted if using a specific structure.
# If 'src.app.tasks' is a package, this helps find tasks in modules within it.
# celery_app.autodiscover_tasks(['src.app.tasks'], related_name='scraper', force=True)

# Example of how you might want to configure task routing if you had multiple queues
# celery_app.conf.task_routes = {
#     'src.app.tasks.scraper.*': {'queue': 'scraping_queue'},
# }

if __name__ == '__main__':
    celery_app.start()
