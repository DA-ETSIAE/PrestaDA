from django.conf import settings
from mozilla_django_oidc.auth import OIDCAuthenticationBackend

from audit.utils import create_audit


class UserAuth(OIDCAuthenticationBackend):
    def create_user(self, claims):
        user = super(UserAuth, self).create_user(claims)
        user.is_logged_by_sso = True
        user.first_name = claims.get('name', '')
        user.email = claims.get('email', '')
        user.save()
        return user

    def update_user(self, user, claims):
        user.is_logged_by_sso = True
        user.first_name = claims.get('name', '')
        user.email = claims.get('email', '')

        user.save()
        return user