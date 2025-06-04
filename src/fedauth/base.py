from django.core.exceptions import ImproperlyConfigured
from mozilla_django_oidc.utils import import_from_settings

from fedauth.federated_providers.mixins import FProviderSettingsMixin


SETTING_NOT_FOUND = "Setting {0} not found for provider with domain '{1}' nor in OIDC common settings"


class ViewBase(FProviderSettingsMixin):
    """
    NOTE - This class should ALWAYS be first in MRO when being inherited by child class, in order for the
    correct 'get_settings' method to be called - `super().get_settings(attr, *args)` will
    call the first `get_setting` method in the MRO, which should be 'get_settings' in this class' parent class.
    """
    OIDC_OP_AUTH_ENDPOINT = None
    OIDC_RP_CLIENT_ID = None

    def get_settings(self, attr, *args):
        try:
            # call FProviderSettingsMixin.get_settings (ensure this class is first in child class MRO)
            return super().get_settings(attr, *args)
        except (ImproperlyConfigured, KeyError):
            # ignore provider specific setting lookup errors, and continue to next step to try and import
            # settings from settings file.
            pass
        try:
            return import_from_settings(attr, *args)
        except ImproperlyConfigured:
            raise ImproperlyConfigured(SETTING_NOT_FOUND.format(attr, self.domain))
