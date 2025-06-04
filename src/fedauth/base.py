from django.core.exceptions import ImproperlyConfigured
from mozilla_django_oidc.utils import import_from_settings

from fedauth.mixins import FProviderSettingsMixin


class ViewBase(FProviderSettingsMixin):
    """
    NOTE!
    Ensure that this class is FIRST in MRO when being inherited.
    """
    OIDC_OP_AUTH_ENDPOINT = None
    OIDC_RP_CLIENT_ID = None

    def get_settings(self, attr, *args):
        try:
            return super().get_settings(attr, *args)
        except (ImproperlyConfigured, KeyError):
            # if not found we'll try to get settings from settings file.
            pass
        try:
            return import_from_settings(attr, *args)
        except ImproperlyConfigured:
            raise ImproperlyConfigured(f"Setting {attr} not found for provider with domain '{self.domain}'")
