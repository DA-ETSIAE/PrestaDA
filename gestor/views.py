from datetime import datetime

from django.contrib import messages
from django.contrib.auth.decorators import user_passes_test, login_required
from django.core.paginator import Paginator
from django.db.models import F, Value, Q
from django.db.models.functions import Concat
from django.http import Http404, HttpResponse, HttpResponseForbidden
from django.shortcuts import render, redirect
from django.urls import reverse
from django.utils import timezone
from django.utils.translation import gettext as _

from audit.models import AuditLog
from audit.utils import create_audit
from gestor.forms import SavePetitionForm, ValidateForm, SaveTypeForm, SaveItemForm
from gestor.models import Item, Type, Petition
from mensajes import utils
from mensajes.models import UserMessage
from usuarios.models import User
from utils import pdfs
from utils.crypto import generate_hash
from utils.table_helper import table_helper, table_helper_status
from . import utils as gu

@user_passes_test(User.staff_check, login_url='login')
def items(request):
    return table_helper(request, Item, ['code', 'type__name' ], 'id', 20, 'items.html', 'partials/tables/items.html', 'items')

@user_passes_test(User.staff_check, login_url='login')
def item_profile(request, iid):
    item = Item.objects.get(id=iid)

    if item is None:
        return Http404

    if request.method != 'POST':
        types = Type.objects.all()
        statii = Item.ItemStatus.choices
        return render(request, 'item_profile.html', {'item': item, 'types': types, 'statii': statii})

    form = SaveItemForm(request.POST or None, instance=item)
    if form.is_valid():
        create_audit(request, AuditLog.AuditTypes.UPDATE, 'Updated User profile')
        form.save()
        return render(request, 'partials/form_success.html', {'msg': _('Updated')})

    return render(request, 'partials/form_error.html', {'form': form})


@user_passes_test(User.staff_check, login_url='login')
def new_item(request):
    if request.method != 'POST':
        types = Type.objects.all()
        statii = Item.ItemStatus.choices
        return render(request, 'item_create.html', {'types': types, 'statii': statii})

    form = SaveItemForm(request.POST)
    if form.is_valid():
        create_audit(request, AuditLog.AuditTypes.CREATE, 'Created Item')
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

    if item.status == Item.ItemStatus.IN_USE:
        return render(request, 'partials/form_error.html', {'error': _('Item assigned')})

    create_audit(request, AuditLog.AuditTypes.DELETE, 'Deleted item')
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
        create_audit(request, AuditLog.AuditTypes.UPDATE, 'Updated type')
        form.save()
        return render(request, 'partials/form_success.html', {'msg': _('Updated')})
    return render(request, 'partials/form_error.html', {'form': form})

@user_passes_test(User.staff_check, login_url='login')
def new_type(request):
    if request.method != 'POST':
        return render(request, 'type_create.html')

    form = SaveTypeForm(request.POST or None)

    if form.is_valid():
        create_audit(request, AuditLog.AuditTypes.CREATE, 'Created type')
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

    create_audit(request, AuditLog.AuditTypes.DELETE, 'Deleted Type')
    type.delete()
    response = HttpResponse()
    response['HX-Redirect'] = reverse('items')
    return response

@login_required(login_url='login')
def petitions(request):
    user_id = request.GET.get('user_id')
    status = request.GET.get('status') or None
    columns = ['type__name', 'user__username', 'user__dni', 'user__email', 'user__username', 'item__code']
    kwargs = {}

    if user_id:
        kwargs['user'] = User.objects.get(id=user_id)

    if status is not None:
        kwargs['add_filters'] = {'status': status}

    return table_helper_status(request, Petition, columns,'-id',20,'petitions.html',
                               'partials/tables/petitions.html', 'petitions', **kwargs)


@login_required(login_url='login')
def reserve(request, tid):
    if request.method != 'POST':
        return render(request, 'partials/store_error.html', {'error': _('errors.invalid_request')})

    user = request.user

    previous_requests = Petition.objects.filter(user=user).filter(Q(status=Petition.PetitionStatus.PENDING) | Q(status=Petition.PetitionStatus.ACTIVE)).count()

    if previous_requests >= user.max_petitions:
        return render(request, 'partials/store_error.html', {'error': _('errors.many_petitions')})

    type = Type.objects.get(pk=tid)

    if type is None:
        return render(request, 'partials/store_error.html', {'error': _('errors.invalid_type')})

    if type.is_blocked is True:
        return render(request, 'partials/store_error.html', {'error': _('errors.blocked_type')})


    petition = Petition.objects.create(type=type, user=user)
    petition.save()

    if (Item.objects.filter(type=type, status=Item.ItemStatus.AVAILABLE).count()
            <= Petition.objects.filter(type=type, status=Petition.PetitionStatus.PENDING).count()):
        type.is_blocked = True
        type.save()

    cnt = _('Petition of %(type)s created') % {'type': type}
    user.message(cnt)

    return render(request, 'partials/store_success.html', {'type': type.name})


@login_required
def petition(request, pid):
    petition = Petition.objects.get(id=pid)
    today = timezone.now()

    if request.method != 'POST':
       if petition is None or ((petition.user != request.user) and (not request.user.is_staff)):
           create_audit(request, AuditLog.AuditTypes.FAIL, 'Tried to access non-own petition')
           return Http404
       items_list = list(Item.objects.filter(type=petition.type).filter(status=Item.ItemStatus.AVAILABLE)) + ([petition.item] if petition.status == petition.PetitionStatus.ACTIVE else [])
       return render(request, 'petition_profile.html',
                     {'petition': petition, 'items': items_list, 'today': today, 'status': Petition.PetitionStatus})

    if not request.user.is_staff:
        create_audit(request, AuditLog.AuditTypes.FAIL, 'Tried to update petition')
        return HttpResponseForbidden()

    if request.POST.get('accept') == 'false':
        petition.status = Petition.PetitionStatus.DECLINED
        petition.save()
        if (Item.objects.filter(type=petition.type, status=Item.ItemStatus.AVAILABLE).count()
                > Petition.objects.filter(type=petition.type, status=Petition.PetitionStatus.PENDING).count()):
            petition.type.is_blocked = False
            petition.type.save()
        return gu.handle_redirect(petition)

    form = SavePetitionForm(request.POST or None, instance=petition)
    if form.is_valid():
        if petition.PetitionStatus.PENDING:
            petition.status = Petition.PetitionStatus.ACTIVE
            petition.date_reserved = timezone.now()
            petition.item.status = Item.ItemStatus.IN_USE
            petition.item.save()
            cnt = _('Petition of %(type)s ACCEPTED') % {'type': petition.type}
            petition.user.message(cnt)

        if petition.PetitionStatus.ACTIVE and request.POST.get('collect') == 'true':
            petition.item.status = Item.ItemStatus.AVAILABLE
            petition.item.save()
            petition.status = Petition.PetitionStatus.COLLECTED
            if (Item.objects.filter(type=petition.type, status=Item.ItemStatus.AVAILABLE).count()
                    > Petition.objects.filter(type=petition.type, status=Petition.PetitionStatus.PENDING).count()):
                petition.type.is_blocked = False
                petition.type.save()
            cnt = _('Petition of %(type)s COLLECTED') % {'type': petition.type}
            petition.user.message(cnt)

        neoitem = form.cleaned_data['item']
        if neoitem != petition.item:
            petition.item.status = Item.ItemStatus.AVAILABLE
            petition.item.save()
            neoitem.status = Item.ItemStatus.IN_USE
            petition.item = neoitem
            neoitem.save()

        petition.save()
        return gu.handle_redirect(petition)

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