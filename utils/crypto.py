import hashlib
import hmac

from django.conf import settings


def generate_hash(dni: str, petition_id: int):
    to_encode = dni + str(petition_id)
    return hmac.new(settings.SECRET_KEY.encode(), to_encode.encode(), hashlib.sha256).hexdigest()