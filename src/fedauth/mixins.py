from mozilla_django_oidc.utils import import_from_settings

from fedauth.utils import get_dynamic_provider_settings, get_static_provider_settings


class AuthBackendSettingsMixin:
    """
    Overrides base class 'get_settings' method
    This get_settings gets settings for both Dynamic and Static OIDC providers
    """
    def get_settings(self, attr, *args):
        """
        If 'domain' in request session, then the user is busy with a dynamic login
        If 'provider' in request session, then the user is busy with a static login
        """
        request = self.request  # NOQA
        domain = request.session.get('domain')
        provider = request.session.get('provider')
        is_dynamic = True if domain else False
        if is_dynamic:
            return get_dynamic_provider_settings(attr, domain, *args)
        elif provider:
            return get_static_provider_settings(attr, provider, *args)
        else:
            # Fallback to global settings or defaults
            return import_from_settings(attr, *args)
