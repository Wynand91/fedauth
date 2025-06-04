from mozilla_django_oidc.views import (
    OIDCAuthenticationRequestView
)

from fedauth.utils import get_non_federated_provider_settings


class AuthenticationRequestView(OIDCAuthenticationRequestView):
    """
    This is the base view for generic oidc views.
    To add new generic oidc, create a new view that inherits from this one and override the alias to match the idp name
    settings definition, e.g:

    class GoogleAuthRequestView(AuthenticationRequestView):
        alias = 'google'

    """
    alias = 'default'

    def get_settings(self, attr, *args):
        return get_non_federated_provider_settings(attr, self.alias, *args)

    def get(self, request):
        # store provider details in session storage. Needed during OIDC callback.
        request.session['provider'] = self.alias
        return super().get(request)
