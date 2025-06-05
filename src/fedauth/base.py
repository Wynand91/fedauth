from django.contrib.auth.backends import UserModel
from django.core.exceptions import ImproperlyConfigured
from mozilla_django_oidc.utils import import_from_settings

from fedauth.utils import get_non_federated_provider_settings, get_federated_provider_settings


class ViewBase:
    """
    Base view used to retrieve config from models
    """
    OIDC_OP_AUTH_ENDPOINT = None
    OIDC_RP_CLIENT_ID = None

    def get_improper_config_err(self, attr):
        raise NotImplementedError()

    def get_model_config(self, attr, *args):
        raise NotImplementedError()

    def get_settings(self, attr, *args):
        try:
            return self.get_model_config(attr,*args)
        except (ImproperlyConfigured, KeyError):
            # if not found we'll try to get settings from settings file.
            pass
        try:
            return import_from_settings(attr, *args)
        except ImproperlyConfigured:
            raise ImproperlyConfigured(self.get_improper_config_err(attr))



class FedViewBase(ViewBase):
    """
    NOTE!
    Ensure that this class is FIRST in MRO when being inherited.
    """
    kwargs = {}
    domain = None

    def get_improper_config_err(self, attr):
        return f"Setting {attr} not found for provider with domain '{self.domain}'"

    def get_model_config(self, attr, *args):
        username = self.kwargs.get(UserModel.USERNAME_FIELD, None)
        if username is None:
            raise ImproperlyConfigured(
                "username field is required in instance kwargs!"
                "Are the kwargs correctly set?"
            )

        domain = username.split('@')[-1]
        self.domain = domain
        return get_federated_provider_settings(attr, domain, *args)



class GenViewBase(ViewBase):
    """
    NOTE!
    Ensure that this class is FIRST in MRO when being inherited.
    """
    alias = None

    def get_improper_config_err(self, attr):
        return f"Setting {attr} not found for provider: '{self.alias}'"

    def get_model_config(self, attr, *args):
        return get_non_federated_provider_settings(attr, self.alias, *args)
