from mozilla_django_oidc.views import (
    OIDCAuthenticationRequestView
)

from fedauth.base import GenViewBase


class GenericAuthenticationRequestView(GenViewBase, OIDCAuthenticationRequestView):
    """
    This is the base view for generic oidc views (e.g. "login with fb").
    To add new generic oidc, create a new view that inherits from this one and override the alias to match the idp name
    settings definition, e.g:

    class FacebookAuthRequestView(AuthenticationRequestView):
        alias = 'fb'

    """
    alias = ''

    def __init__(self, *args, **kwargs):  # noqa
        # skip super init, so that it doesn't try to load values the default way (from settings config - we load
        # settings from model object.)
        pass

    def get(self, request, **kwargs):
        # since attributes weren't set during init, we can do it here.
        self.OIDC_OP_AUTH_ENDPOINT = self.get_settings('OIDC_OP_AUTHORIZATION_ENDPOINT')
        self.OIDC_RP_CLIENT_ID = self.get_settings('OIDC_RP_CLIENT_ID')
        # store provider details in session storage. Needed during OIDC callback.
        request.session['provider'] = self.alias
        return super().get(request)
