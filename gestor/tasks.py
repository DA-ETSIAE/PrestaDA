from celery import shared_task
from celery.utils.log import get_task_logger
from django.utils import timezone
from django.utils.translation import gettext as _

logger = get_task_logger(__name__)

@shared_task
def check_expired_petitions():
    from gestor.models import Petition

    now = timezone.now()
    expired = Petition.objects.filter(status=Petition.Status.ACTIVE, until__lt=timezone.now())
    header = _('Loan Expired')
    
    for p in expired:
        p.status = Petition.Status.EXPIRED
        p.save()
        
        msg = _('Your loan of %(type)s has expired') % {'type': p.type.name}
        p.user.message(msg, False, header)

    logger.info('Updated Petitions')
