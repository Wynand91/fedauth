from mozilla_django_oidc.utils import import_from_settings

from fedauth.constants import SETTINGS_MAP
from fedauth.models import DynamicProvider, StaticProvider


def get_provider_config(provider, attr, *args):
    # Most settings are stored on te model, but some settings are global settings defined in config
    try:
        attr = SETTINGS_MAP[attr]
    except KeyError:
        # check for global settings if setting not in map
        return import_from_settings(attr, *args)

    if args:
        return getattr(provider, attr, args[0])
    return getattr(provider, attr)


def get_dynamic_provider_settings(attr, domain, *args):
    provider = DynamicProvider.objects.get(domain=domain)
    return get_provider_config(provider, attr, *args)


def get_static_provider_settings(attr, alias, *args):
    provider = StaticProvider.objects.get(provider=alias)
    return get_provider_config(provider, attr, *args)
