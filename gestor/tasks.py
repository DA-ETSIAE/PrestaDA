from celery import shared_task
from celery.utils.log import get_task_logger
from django.utils import timezone

logger = get_task_logger(__name__)

@shared_task
def check_expired():
    from gestor.models import Petition
    count = Petition.objects.filter(status=Petition.PetitionStatus.ACTIVE, until__lt=timezone.now()).update(status=Petition.PetitionStatus.EXPIRED)

    if count:
        logger.info(f'Updated {count} Petitions')