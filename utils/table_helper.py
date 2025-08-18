from typing import List, Optional, Dict, Any

from django.core.paginator import Paginator
from django.db.models import Q
from django.shortcuts import render

from usuarios.models import User


def find(request, model, fields):
    search = request.GET.get('s', '').strip()

    if search:
        query = Q()
        for field in fields:
            query |= Q(**{f'{field}__icontains': search})
        return model.objects.filter(query)
    return model.objects.all()


def paginate(page, models, per_page):
    paginator = Paginator(models, per_page)
    page_obj = paginator.get_page(page)
    return page_obj


def table_helper(request, model, fields: List[str], order_by,  per_page, full, partial, context, add_filters: Optional[Dict[str, Any]] = None, user: Optional[User] = None):
    models = find(request, model, fields).order_by(order_by)

    if user:
        models = models.filter(user=user)

    if add_filters:
        models = models.filter(**add_filters)

    page_obj = paginate(request.GET.get('p', 1), models, per_page)

    if request.headers.get('HX-Request') == 'true':
        return render(request, partial, {context: page_obj})

    return render(request, full, {context: page_obj})
