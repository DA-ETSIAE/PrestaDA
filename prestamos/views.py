from django.db.models import Q
from django.http import HttpResponse
from django.utils import timezone

from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404

import configuracion.models
from gestor.models import Petition, Type as GestorType, Item
from mensajes.models import UserMessage, GlobalMessage
from utils import pdfs
from utils.colors import match_color


@login_required(login_url='login')
def index(request):
    user_petitions = Petition.objects.filter(user=request.user).filter(Q(status=Petition.PetitionStatus.PENDING) | Q(status=Petition.PetitionStatus.ACTIVE))
    user_messages = UserMessage.objects.filter(user=request.user).filter(is_read=False).order_by('-date_created')[:10]
    global_messages = GlobalMessage.objects.filter(is_active=True)

    today = timezone.now()

    for user_petition in user_petitions:
        if user_petition.status == Petition.PetitionStatus.ACTIVE:
            delta = (user_petition.until - today).days
            total = max((user_petition.until - user_petition.date_reserved).days, 1)
            percent = min(int((1 - delta/total)*100), 100)
            user_petition.percent = percent
            user_petition.color = match_color(percent)

    return render(request, 'index.html', {'user_petitions': user_petitions,
                                          'user_messages': user_messages, 'global_messages': global_messages,
                                          'message_count': len(user_messages), 'status': Petition.PetitionStatus})

@login_required(login_url='login')
def store(request):
    search = request.GET.get('s','')
    types = GestorType.objects.all()

    if search:
        types = types.filter(Q(name__icontains=search) | Q(description__icontains=search))

    if request.headers.get("HX-Request") == "true":
        return render(request, 'partials/results.html', {'gestor_types': types})

    return render(request, 'store.html', {'gestor_types': types})



@login_required(login_url='login')
def print_profile(request, id):
    petition = get_object_or_404(Petition, id=id)

    if petition.user != request.user and not request.user.is_staff:
        return HttpResponse(status=403)

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'inline; filename="documento.pdf"'

    pdfs.generate_invoice(response, petition)
    return response
