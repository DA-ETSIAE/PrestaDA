from celery import shared_task
from celery.utils.log import get_task_logger
from django.utils import timezone
from django.utils.translation import gettext as _

logger = get_task_logger(__name__)

@shared_task
def check_expired_petitions():
    from gestor.models import Petition
    count = Petition.objects.filter(status=Petition.Status.ACTIVE, until__lt=timezone.now()).update(status=Petition.Status.EXPIRED)

    header = _('Loan Expired')
    for p in Petition.objects.filter(status=Petition.Status.EXPIRED):
        msg = _('Your loan of %(type)s has expired') % {'type': p.type.name}
        p.user.message(msg, False, header)

    if count:
        logger.info(f'Updated {count} Petitions')