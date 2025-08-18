from django.contrib.auth.decorators import login_required, user_passes_test
from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404

from configuracion import models
from configuracion.models import Configuration, ConfigForm
from usuarios.models import User


@user_passes_test(User.staff_check, 'login')
def settings_page(request):

        configs = Configuration.objects.all()
        context = {
            'configs': configs,
        }
        return render(request, 'settings.html', context)

@user_passes_test(User.superuser_check, 'login')
def save_config(request, node):
    config = get_object_or_404(Configuration, node=node)
    form = ConfigForm(request.POST or None, instance=config)

    if form.is_valid():
        print(form.cleaned_data['value'])
        config.value = form.cleaned_data['value']
        config.save()

        return render(request, 'partials/form_success.html')
    else:
        return render(request, 'partials/form_error.html', {'form': form})