from mozilla_django_oidc.views import (
    OIDCAuthenticationRequestView
)

from fedauth.base import DynamicViewBase


class DynamicAuthenticationRequestView(DynamicViewBase, OIDCAuthenticationRequestView):
    """
    OIDCAuthenticationRequestView with alternate 'get_settings' functionality.
    """
    domain = ''

    def __init__(self, *args, **kwargs):  # NOQA
        # skip super __init__. It tries to set class variables before username kwarg is available.
        # Attributes are instead set during `get` method.
        pass

    def get(self, request, **kwargs):
        self.kwargs = kwargs
        self.OIDC_OP_AUTH_ENDPOINT = self.get_settings("OIDC_OP_AUTHORIZATION_ENDPOINT")
        self.OIDC_RP_CLIENT_ID = self.get_settings("OIDC_RP_CLIENT_ID")
        return super().get(request)
