from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from mozilla_django_oidc.utils import import_from_settings

from fedauth.federated_providers.constants import SETTINGS_MAP
from fedauth.federated_providers.models import FederatedProvider


def get_federated_provider_settings(attr, domain, *args):
    provider = FederatedProvider.objects.get(domain=domain)

    try:
        attr = SETTINGS_MAP[attr]
    except KeyError:
        # check for global settings if setting not in map
        return import_from_settings(attr, *args)

    if args:
        return getattr(provider, attr, args[0])
    return getattr(provider, attr)


def get_non_federated_provider_settings(attr, alias, *args):
    try:
        # first check if it's a generic setting, but don't use default arg if not found just yet.
        return getattr(settings, attr)
    except AttributeError:
        pass

    # secondly, check for specific provider settings
    oidc_settings = getattr(settings, "OIDC_PROVIDERS")
    provider_settings = oidc_settings.get(alias)

    try:
        if args:
            return provider_settings.get(attr, args[0])
        return provider_settings[attr]
    except (KeyError, AttributeError):
        err_mssg = "Setting {0} not found for provider alias '{1}' nor in OIDC common settings"
        raise ImproperlyConfigured(err_mssg.format(attr, alias))
