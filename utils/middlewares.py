from django.conf import settings
from django.contrib.auth import login, logout
from django.contrib.auth.views import logout_then_login
from django.http import HttpResponse
from django.shortcuts import redirect, render
from django.urls import reverse, reverse_lazy

from audit.utils import create_audit
from configuracion.models import Configuration
from usuarios.models import User
import os 


class MaintenanceMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        path = request.path

        if (path.startswith('/static') or path.startswith('/media') or path.startswith('/login')
                or path.startswith('/oidc') or path.startswith('/logout') or path.startswith('/admin') or path.startswith('/local') ):
            return self.get_response(request)

        if request.user.is_authenticated and (request.user.can_bypass_maint or request.user.is_staff):
            return self.get_response(request)

        if Configuration.objects.get(node='maintenance_kind').value == "True":
            return render(request, 'maintenance.html')

        if Configuration.objects.get(node='maintenance_ugly').value == 'True':
            return HttpResponse(status=int(Configuration.objects.get(node='maintenance_ugly_code').value))

        return self.get_response(request)


class NewUserMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        path = request.path

        if path.startswith('/static') or path.startswith('/media') or path.startswith('/users/profile') or path.startswith('/oidc') or path.startswith('/setup') or path.startswith('/logout'):
            return self.get_response(request)

        if request.user.is_authenticated and getattr(request.user, "is_new_user", True):
            return redirect('profile_self')

        return self.get_response(request)


class BanMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        path = request.path

        if path.startswith('/banned'):
            return self.get_response(request)

        if request.user.is_authenticated and request.user.is_banned:
            return redirect('banned')

        return self.get_response(request)


class ScriptNameMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        prefix = os.environ.get("FORCE_SCRIPT_NAME", "/prestamos")
        request.META["SCRIPT_NAME"] = prefix
        if request.path.startswith(prefix):
            request.path_info = request.path[len(prefix):] or "/"
        return self.get_response(request)



