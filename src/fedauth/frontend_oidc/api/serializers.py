from django.core.cache import cache
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from fedauth.frontend_oidc.utils import build_oidc_auth_url
from fedauth.models import StaticProvider, DynamicProvider


def get_provider_options():
    providers = StaticProvider.objects.all()
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
            for p in StaticProvider.objects.all()
        ]

    def populate_auth_url(self, attrs):
        auth_url = None
        # if username field is populated in payload - It's a dynamic login
        username = attrs.get('username')
        request = self.context['request']
        if username:
            domain = username.split('@')[-1]
            provider = DynamicProvider.objects.filter(domain=domain)
            if provider.exists():
                auth_url = build_oidc_auth_url(request, provider.first())
        else:
            # if there is no username in post data - we assume that it isn't a dynamic login ('Login with x')
            gen_provider = attrs.get('provider')
            provider = StaticProvider.objects.filter(provider=gen_provider)
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


class TokenExchangeSerializer(serializers.Serializer):
    code = serializers.CharField(max_length=64)

    def validate(self, attrs):
        request = self.context['request']
        code = request.data.get('code')
        jwt_token = cache.get(f'auth_code:{code}')
        if not jwt_token:
            raise ValidationError({'detail': 'Code Invalid or expired'})
        cache.delete(f'auth_code:{code}')
        # add tokens to attrs (jwt_token contains access and refresh tokens)
        attrs['tokens'] = jwt_token
        return attrs
