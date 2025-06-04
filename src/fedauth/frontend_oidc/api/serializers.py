from django.conf import settings
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from fedauth.federated_oidc.models import FederatedProvider
from fedauth.frontend_oidc.utils import build_oidc_auth_url


def get_provider_options():
    providers = settings.OIDC_PROVIDERS
    return [(key, key) for key in providers.keys()]


class LoginSerializer(serializers.Serializer):
    """
    Request data should only contain username OR provider. Not both.
    """
    username = serializers.EmailField(required=False)
    provider = serializers.ChoiceField(choices=get_provider_options(), required=False)

    def populate_auth_url(self, attrs):
        auth_url = None
        # if username field is populated in payload - It's a federated login
        username = attrs.get('username')
        request = self.context['request']
        if username:
            domain = username.split('@')[-1]
            provider = FederatedProvider.objects.filter(domain=domain)
            if provider.exists():
                auth_url = build_oidc_auth_url(request, provider.first())
        else:
            # if there is no username in post data - we assume that it isn't a federated username ('Login with x')
            provider = attrs.get('provider')
            auth_url = build_oidc_auth_url(request, provider)
        attrs['auth_url'] = auth_url

    def validate(self, attrs):
        username = attrs.get('username')
        provider = attrs.get('provider')
        if username and provider:
            raise ValidationError('Submit either username OR provider, not both.')
        if not username and not provider:
            raise ValidationError('Must submit either username OR provider')
        # populated validated data with idp url
        self.populate_auth_url(attrs)
        return attrs


