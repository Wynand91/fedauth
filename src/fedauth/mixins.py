from abc import ABC

from django.contrib.auth.backends import UserModel
from django.core.exceptions import ImproperlyConfigured

from fedauth.utils import get_federated_provider_settings, get_non_federated_provider_settings


class AuthBackendSettingsMixin:
    """
    Overrides base class 'get_settings' method
    This get_settings gets settings for both federated and non-federated OIDC providers
    """
    def get_settings(self, attr, *args):
        request = self.request  # NOQA
        domain = request.session.get('domain')
        provider = request.session.get('provider')

        is_federated = True if domain else False
        if is_federated:
            return get_federated_provider_settings(attr, domain, *args)
        else:
            # assume non-federated OIDC login
            return get_non_federated_provider_settings(attr, provider, *args)
