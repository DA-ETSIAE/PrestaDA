from django.contrib.auth.decorators import user_passes_test
from django.shortcuts import render

from audit.models import AuditLog
from usuarios.models import User
from utils.table_helper import table_helper, table_helper_status


@user_passes_test(User.superuser_check, 'login')
def logs(request):
    audit_type = request.GET.get('audit_type') or None
    columns = ['user__email', 'description']
    kwargs = {}
    if audit_type is not None:
        kwargs['add_filters'] = {'audit_type': audit_type}

    return table_helper_status(request, AuditLog, columns, '-id', 40, 'audit.html',
                               'partials/tables/logs.html', 'logs', statii=AuditLog.AuditTypes.choices, **kwargs)

