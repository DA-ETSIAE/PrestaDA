from celery import shared_task
from celery.utils.log import get_task_logger
from django.db.models import Q

logger = get_task_logger(__name__)

@shared_task
def check_waiting_users():
    from usuarios.models import User
    count = User.objects.filter(Q(dni__isnull=True) | Q(phone__isnull=True)).delete()

    if count:
        logger.info(f'Deleted {count} users')
