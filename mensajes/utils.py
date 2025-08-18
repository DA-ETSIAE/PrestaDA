from typing import Optional


from django.core.mail import send_mail

from configuracion.models import Configuration
from mensajes.models import UserMessage
from prestamos import settings
from usuarios.models import User


def send_message(user: User, content: str, is_from_staff: Optional[bool] = False, email_subject: Optional[str] = None):
    message = UserMessage.objects.create(user=user, content=content, is_from_staff=is_from_staff)
    message.save()

    if email_subject:
        send_mail(email_subject, content, settings.EMAIL_HOST_USER, [user.email])

def send_admin_message(content: str, email_subject: str):
    send_mail(email_subject, content, Configuration.objects.get(node="smtp_email").value, [Configuration.objects.get(node="contact_email").value])