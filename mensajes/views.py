
from django.contrib.auth.decorators import login_required, user_passes_test
from django.http import HttpResponse
from django.shortcuts import render
from django.urls import reverse

from audit.models import AuditLog
from audit.utils import create_audit
from configuracion.models import Configuration
from mensajes import forms, utils
from mensajes.forms import UserForm
from mensajes.models import UserMessage, GlobalMessage
from usuarios.models import User
from django.utils.translation import gettext as _

@login_required(login_url='login')
def read(request, mid):
    if request.method != 'POST':
        return HttpResponse(status=403)

    msg = UserMessage.objects.get(user=request.user, id=mid)

    if msg is None:
        return render(request, 'partials/form_error_other.html')

    msg.is_read = True
    msg.save()

    response = HttpResponse()
    response['HX-Redirect'] = reverse('index')
    return response


@user_passes_test(User.superuser_check, login_url='login')
def send_global(request):
    if request.method != 'POST':
        colors = GlobalMessage.Colors.choices
        return render(request, 'message_global.html', {'colors': colors})

    form = forms.GlobalForm(request.POST or None)

    if form.is_valid():
        message = form.save(commit=False)
        if message.title is None:
            message.has_title = False
        message.save()
        create_audit(request, AuditLog.AuditTypes.CREATE, 'Sent global message')
        return render(request, 'partials/form_success.html')

    return render(request, 'partials/form_error.html', {'form': form})

@user_passes_test(User.superuser_check, login_url='login')
def delete_global(request):
    if request.method != 'POST':
        return HttpResponse(status=404)

    msg = GlobalMessage.objects.get(id=request.POST.get('id'))
    msg.is_active = False
    msg.save()
    create_audit(request, AuditLog.AuditTypes.DELETE, 'Deleted global message')
    response = HttpResponse()
    response['HX-Redirect'] = reverse('index')
    return response


@user_passes_test(User.superuser_check, login_url='login')
def send_user(request, uid):
    user = User.objects.get(id=uid)
    if request.method != 'POST':
        return render(request, 'message_user.html', {'user': user})

    form = UserForm(request.POST or None)

    if form.is_valid():
        message = form.cleaned_data['content']
        header = _('Admin Message')
        utils.send_message(user, message, is_from_staff=True, email_subject=header)
        create_audit(request, AuditLog.AuditTypes.CREATE, 'Messaged user')
        return render(request, 'partials/form_success.html')

    return render(request, 'partials/form_error.html', {'form': form})



