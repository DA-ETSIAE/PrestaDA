from django.contrib.admin.views.decorators import staff_member_required
from ninja import NinjaAPI
from ninja.security import django_auth_superuser
from pip._internal import configuration

import configuracion.api

api = NinjaAPI(title='Prestamos API', version='1.0', csrf=True, docs_decorator=staff_member_required)

@api.get("/health")
def healthcheck(request):
    return {"status": "OK"}

api.add_router('/config/', configuracion.api.router)
