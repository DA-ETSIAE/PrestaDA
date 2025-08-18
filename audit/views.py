from django.contrib.auth.decorators import user_passes_test
from django.shortcuts import render

from audit.models import AuditLog
from usuarios.models import User
from utils.table_helper import table_helper


@user_passes_test(User.superuser_check, 'login')
def logs(request):
    return table_helper(request, AuditLog, ['user__email', 'audit_type', 'description'], '-created_at', 20, 'audit.html','partials/tables/logs.html', 'logs')