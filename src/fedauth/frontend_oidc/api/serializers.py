from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from fedauth.federated_oidc.models import FederatedProvider
from fedauth.frontend_oidc.utils import build_oidc_auth_url
from fedauth.generic_oidc.models import GenericProvider


def get_provider_options():
    providers = GenericProvider.objects.all()
    return [(prov.provider, prov.provider) for prov in providers]


class LoginSerializer(serializers.Serializer):
    """
    Request data should only contain username OR provider. Not both.
    """
    username = serializers.EmailField(required=False)
    provider = serializers.ChoiceField(choices=[], required=False)  # choices are dynamically loaded below

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['provider'].choices = self.get_provider_choices()

    @staticmethod
    def get_provider_choices():
        """
        The serializer by default caches 'ChoiceField.choices' the first time it is initialized. This
        can be problematic, since providers can be added on admin page, and the new choices
        won't reflect until cache expires. So we need to dynamically get choices every time the serializer is
        initialized by calling this method in __init__
        """
        return [
            (p.provider, p.provider)
            for p in GenericProvider.objects.all()
        ]

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
            gen_provider = attrs.get('provider')
            provider = GenericProvider.objects.filter(provider=gen_provider)
            if provider.exists():
                auth_url = build_oidc_auth_url(request, provider.first())
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


