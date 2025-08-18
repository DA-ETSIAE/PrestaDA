from datetime import datetime

from django.contrib import messages
from django.contrib.auth.decorators import user_passes_test, login_required
from django.core.paginator import Paginator
from django.db.models import F, Value, Q
from django.db.models.functions import Concat
from django.http import Http404, HttpResponse
from django.shortcuts import render, redirect
from django.urls import reverse
from django.utils import timezone
from django.utils.translation import gettext as _

from audit.utils import create_audit
from gestor.forms import SavePetitionForm, ValidateForm, SaveTypeForm, SaveItemForm
from gestor.models import Item, Type, Petition
from mensajes import utils
from mensajes.models import UserMessage
from usuarios.models import User
from utils import pdfs
from utils.crypto import generate_hash
from utils.table_helper import table_helper


@user_passes_test(User.staff_check, login_url='login')
def items(request):
    return table_helper(request, Item, ['code', 'type__name' ], 'id', 5, 'items.html', 'partials/tables/items.html', 'items')

@user_passes_test(User.staff_check, login_url='login')
def item_profile(request, iid):
    item = Item.objects.get(id=iid)

    if item is None:
        return Http404

    if request.method != 'POST':
        types = Type.objects.all()
        return render(request, 'item_profile.html', {'item': item, 'types': types})

    form = SaveItemForm(request.POST or None, instance=item)

    if form.is_valid():
        create_audit(request, "UPDATE", 'item_profile ' + item.code)
        form.save()
        return render(request, 'partials/form_success.html', {'msg': _('Updated')})
    return render(request, 'partials/form_error.html', {'form': form})


@user_passes_test(User.staff_check, login_url='login')
def new_item(request):
    if request.method != 'POST':
        types = Type.objects.all()
        return render(request, 'item_create.html', {'types': types})

    form = SaveItemForm(request.POST)
    if form.is_valid():
        create_audit(request, "CREATE", 'new_item ' + form.cleaned_data['code'])
        form.save()
        response = HttpResponse()
        response['HX-Redirect'] = reverse('items')
        return response

    return render(request, 'partials/form_error.html', {'form': form})

@user_passes_test(User.superuser_check, login_url='login')
def delete_item(request):
    if request.method != 'POST':
        return HttpResponse(status=404)

    print(request.POST.get('value'))
    item = Item.objects.get(id=request.POST.get('id'))

    if not item:
        return render(request, 'partials/form_error.html', {'error': _('Item invalid')})

    if not item.is_available:
        return render(request, 'partials/form_error.html', {'error': _('Item assigned')})

    create_audit(request, "REMOVE", 'delete_item ' + item.code)
    item.delete()
    response = HttpResponse()
    response['HX-Redirect'] = reverse('items')
    return response



@login_required(login_url='login')
def types(request):
    return table_helper(request, Type, ['name', 'description'], 'id', 5, 'types.html', 'partials/tables/types.html','types')

@user_passes_test(User.staff_check, login_url='login')
def type_profile(request, tid):
    if tid is None:
        return HttpResponse(status=418)

    type = Type.objects.get(id=tid)

    if type is None:
        return Http404

    if request.method != 'POST':
        return render(request, 'type_profile.html', {'type': type})

    form = SaveTypeForm(request.POST or None, instance=type)

    if form.is_valid():
        create_audit(request, "UPDATE", 'type_profile ' + form.cleaned_data['name'])
        form.save()
        return render(request, 'partials/form_success.html', {'msg': _('Updated')})
    return render(request, 'partials/form_error.html', {'form': form})

@user_passes_test(User.staff_check, login_url='login')
def new_type(request):
    if request.method != 'POST':
        return render(request, 'type_create.html')

    form = SaveTypeForm(request.POST or None)

    if form.is_valid():
        create_audit(request, "UPDATE", 'type_profile ' + form.cleaned_data['name'])
        form.save()
        response = HttpResponse()
        response['HX-Redirect'] = reverse('items')
        return response

    return render(request, 'partials/form_error.html', {'form': form})

@user_passes_test(User.superuser_check, login_url='login')
def delete_type(request):
    if request.method != 'POST':
        return HttpResponse(status=404)

    type = Type.objects.get(id=request.POST.get('id'))

    if not type:
        return render(request, 'partials/form_error.html', {'error': _('type invalid')})

    petitions = Petition.objects.filter(type=type)

    if petitions is not None:
        return render(request, 'partials/form_error.html', {'error': _('type being used')})

    create_audit(request, "UPDATE", 'type_profile ' + type.name)
    type.delete()
    response = HttpResponse()
    response['HX-Redirect'] = reverse('items')
    return response

@login_required(login_url='login')
def petitions(request):
    only_active = request.GET.get('active_filter') == 'on'
    only_pending = not request.GET.get('pending_filter') == 'on'
    expired = request.GET.get('expired_filter') == 'on'
    user_id = request.GET.get('user_id')

    if not user_id:
        if not expired:
            return table_helper(request, Petition,
                       ['type__name', 'user__username', 'user__dni', 'user__email', 'user__username', 'item__code'],
                       '-id', 10, 'petitions.html', 'partials/tables/petitions.html', 'petitions',
                       add_filters={'is_active': only_active, 'is_pending': only_pending})
        today = timezone.now()
        return table_helper(request, Petition,
                            ['type__name', 'user__username', 'user__dni', 'user__email', 'user__username',
                             'item__code'],
                            '-id', 10, 'petitions.html', 'partials/tables/petitions.html', 'petitions',
                            add_filters={'is_active': only_active, 'is_pending': only_pending, 'until__lt': today})

    user = User.objects.get(id=user_id)
    return table_helper(request, Petition,
                     ['type__name', 'user__username', 'user__dni', 'user__email', 'user__username', 'item__code'],
                    '-id', 10, 'petitions.html', 'partials/tables/petitions.html', 'petitions',
                            add_filters={'is_active': only_active, 'is_pending': only_pending}, user=user)


@login_required(login_url='login')
def reserve(request, tid):
    if request.method != 'POST':
        return render(request, 'partials/store_error.html', {'error': _('errors.invalid_request')})

    user = request.user

    previous_requests = Petition.objects.filter(user=user).filter(is_pending=True).count() + Petition.objects.filter(user=user).filter(is_active=True).count()

    if previous_requests >= user.max_petitions:
        return render(request, 'partials/store_error.html', {'error': _('errors.many_petitions')})

    type = Type.objects.get(pk=tid)

    if type is None:
        return render(request, 'partials/store_error.html', {'error': _('errors.invalid_type')})

    if type.is_blocked is True:
        return render(request, 'partials/store_error.html', {'error': _('errors.blocked_type')})

    petition = Petition.objects.create(type=type, user=user)
    petition.save()

    cnt = _('Petition of %(type)s created') % {'type': type}
    utils.send_message(user, cnt)

    return render(request, 'partials/store_success.html', {'type': type.name})


@login_required
def petition(request, pid):
    petition = Petition.objects.get(id=pid)

    if request.user != petition.user and not request.user.is_staff:
        return redirect('index')

    if request.method != 'POST':
        if petition is None:
            return Http404

        if (petition.user != request.user) and (not request.user.is_staff):
            return Http404

        items = list(Item.objects.filter(type=petition.type).filter(is_available=True).filter(is_blocked=False))

        if petition.is_active:
            items.append(petition.item)

        today = timezone.now()

        return render(request, 'petition_profile.html', {'petition': petition, 'items': items, 'today': today})

    if not request.user.is_staff:
        return HttpResponse(status=403)

    form = SavePetitionForm(request.POST or None, instance=petition)
    if petition.is_pending:
        # DECLINE
        if request.POST.get('accept') == 'false':
            petition.is_pending = False
            petition.is_active = False
            petition.save()
            utils.send_message(petition.user, _('Petition of %(type)s declined') % {'type': petition.type})
            response = HttpResponse()
            response['HX-Redirect'] = reverse('petition', args=[pid])
            return response

        # ACCEPT
        if form.is_valid():
            if not form.cleaned_data['item']:
                return render(request, 'partials/form_error.html', {'error': _('specify id')})
            item = form.cleaned_data['item']
            create_audit(request, "UPDATE", 'petition ' + petition.user.username)
            petition.is_active = True
            petition.is_pending = False
            petition.date_reserved = timezone.now()
            petition.save()
            item.is_available = False
            item.save()
            utils.send_message(petition.user, _('Petition of %(type)s accepted') % {'type': petition.type})
            response = HttpResponse()
            response['HX-Redirect'] = reverse('petition', args=[pid])
            return response

    if petition.is_active and form.is_valid():
        # COLLECT
        if request.POST.get('collect') == 'true':
            create_audit(request, "REMOVE", 'petition ' + petition.user.username)
            petition.is_active = False
            petition.item.is_available = True
            petition.item.save()
            petition.item = None
            petition.save()
            utils.send_message(petition.user, _('Petition of %(type)s collected') % {'type': petition.type})
            response = HttpResponse()
            response['HX-Redirect'] = reverse('petition', args=[pid])
            return response
        # EDIT
        if not form.cleaned_data['item']:
            return render(request, 'partials/form_error.html', {'error': _('specify id')})
        item = form.cleaned_data['item']
        if item != petition.item:
            item.is_available = False
            petition.item.is_available = True
            item.save()
            petition.item.save()
        create_audit(request, "UPDATE", 'petition ' + petition.user.username)
        utils.send_message(petition.user, _('Petition of %(type)s edited') % {'type': petition.type})
        petition.save()
        response = HttpResponse()
        response['HX-Redirect'] = reverse('petition', args=[pid])
        return response
    # BAD
    return render(request, 'partials/form_error.html', {'form': form})

@user_passes_test(User.staff_check, login_url='login')
def validate(request):
    if request.method != 'POST':
        return render(request, 'validate.html')

    form = ValidateForm(request.POST or None)

    if form.is_valid():
        dni = form.cleaned_data['dni']
        pid = form.cleaned_data['pid']
        hashed = form.cleaned_data['hashed']
        if hashed == generate_hash(dni, pid):
            print(generate_hash(dni, pid))
            return render(request,'partials/form_success.html')
        else:
            return render(request, 'partials/form_error.html', {'error': _('errors.doesnt_match')})
    return render(request, 'partials/form_error.html', {'form': form})

@user_passes_test(User.superuser_check, login_url='login')
def print_list(request):
    if request.method != 'POST':
        types = Type.objects.all()
        return render(request, 'print.html', {'types': types})

    start_date = request.POST.get('start_date')
    end_date = request.POST.get('end_date')

    start_date = datetime.strptime(start_date, "%Y-%m-%d").date()
    end_date = datetime.strptime(end_date, "%Y-%m-%d").date()

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'inline; filename="documento.pdf"'

    type = request.POST.get('type')
    type = Type.objects.get(id=type) if type else None
    pdfs.generate_registry(response, start_date, end_date, type)
    return response