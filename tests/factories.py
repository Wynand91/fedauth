from factory.django import DjangoModelFactory

from fedauth.models import FederatedProvider, GenericProvider


class FederatedProviderFactory(DjangoModelFactory):
    domain = 'company.com'
    auth_endpoint = 'https://oauth.id.okta.com/oauth2/auth'
    token_endpoint = 'https://oauth.id.okta.com/oauth2/token'
    user_endpoint = 'https://oauth.id.okta.com/userinfo'
    jwks_endpoint = 'https://oauth.id.okta.com/keys'
    client_id = '5e7b657f-ac86-45de-9755-c9e1ee6c4d93'
    client_secret = 'HWcI.p6WmTqCv6.OHtG3Dp0~Ep'
    sign_algo = 'HS256'

    class Meta:
        model = FederatedProvider


class GenericProviderFactory(DjangoModelFactory):
    provider = 'jumpcloud'
    auth_endpoint = 'https://oauth.id.jumpcloud.com/oauth2/auth'
    token_endpoint = 'https://oauth.id.jumpcloud.com/oauth2/token'
    user_endpoint = 'https://oauth.id.jumpcloud.com/userinfo'
    jwks_endpoint = 'https://oauth.id.jumpcloud.com/keys'
    client_id = '5e7b657f-ac86-45de-9755-c9e1ee6c4d93'
    client_secret = 'HWcI.p6WmTqCv6.OHtG3Dp0~Ep'
    sign_algo = 'HS256'

    class Meta:
        model = GenericProvider
