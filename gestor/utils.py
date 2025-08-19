from django.http import HttpResponse
from django.urls import reverse

from gestor.models import Petition


def handle_redirect(petition: Petition):
    response = HttpResponse()
    response['HX-Redirect'] = reverse('petition', args=[petition.id])
    return response