from django.contrib.auth import login
from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.paginator import Paginator
from django.http import HttpResponse, HttpResponseNotFound, Http404
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.utils import timezone

from audit.models import AuditLog
from audit.utils import create_audit
from gestor.models import Petition
from prestamos import settings
from usuarios.models import User, SetupForm, BanForm
from utils.environment import get_env_bool
from utils.table_helper import table_helper
from gettext import gettext as _

def login_page(request):
    if request.user.is_authenticated:
        return redirect('index')
    else:
        return render(request, 'login.html')

def local_login(request):
    if settings.DEBUG and get_env_bool('PRESTAMOS_LOCALMODE'):
        user = User.objects.get_or_create(is_local_user=True)[0]
        user.backend = 'usuarios.auth.UserAuth'
        user.is_staff = True
        user.is_superuser = True
        user.username = "Local Dev"
        user.first_name = "Local"
        user.is_local_user = True
        user.save()
        login(request, user)
        create_audit(request, AuditLog.AuditTypes.URGENT, 'local_login ')
        return redirect('index')
    else:
        return HttpResponse(status=403)


@user_passes_test(User.staff_check, 'login')
def users(request):
    return table_helper(request, User, ['username', 'dni', 'phone', 'email'], 'date_joined', 5, 'users.html','partials/tables/users.html', 'users')

@login_required(login_url='login')
def profile_id(request, pid):
    user = User.objects.get(id=pid)
    statii = Petition.PetitionStatus.choices
    if user is None or (user.id != request.user.id and not request.user.is_staff):
        return Http404
    return render(request, 'profile.html', {'user': user, 'statii': statii})

@login_required
def profile(request):
    return profile_id(request, request.user.id)

@login_required(login_url='login')
def setup(request):
    user = request.user
    form = SetupForm(request.POST or None, instance=user)

    if not user.is_new_user:
        response = HttpResponse()
        response['HX-Redirect'] = reverse('index')
        return response

    if form.is_valid():
        user = form.save(commit=False)
        user.is_new_user = False
        user.save()
        response = HttpResponse()
        response['HX-Redirect'] = reverse('index')
        return response
    else:
        return render(request, 'partials/form_error.html', {'form': form})

@user_passes_test(User.superuser_check, 'login')
def ban(request, pid):
    target = User.objects.get(id=pid)

    if target is None:
        return Http404

    if request.method != 'POST':
        return render(request, 'ban.html', {'target': target})

    form = BanForm(request.POST or None, instance=target)

    if form.is_valid():
        target = form.save(commit=False)
        target.banned_at = timezone.now()
        target.is_banned = True
        target.save()
        create_audit(request, AuditLog.AuditTypes.UPDATE, 'Banned ' + target.username)
        response = HttpResponse()
        response['HX-Redirect'] = reverse('profile', args=[target.id])
        return response
    else:
        return render(request, 'partials/form_error.html', {'form': form})

@login_required(login_url='login')
def banned(request):
    user = request.user

    if not request.user.is_banned:
        return redirect('index')

    return render(request, 'banned.html', {'user': user})

@user_passes_test(User.superuser_check, 'login')
def make_staff(request):
    user = User.objects.get(id=request.POST.get('user'))

    if user is None:
        return render(request, 'partials/form_error.html', {'error': _('user invalid')})

    create_audit(request, AuditLog.AuditTypes.UPDATE, 'Made staff ' + user.username)
    user.is_staff = not user.is_staff
    user.save()
    response = HttpResponse()
    response['HX-Redirect'] = reverse('profile', args=[user.id])
    return response
