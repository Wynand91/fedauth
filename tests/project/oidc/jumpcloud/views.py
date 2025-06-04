from fedauth.generic_oidc.views import AuthenticationRequestView

ALIAS = 'jumpcloud'


class JumpcloudAuthenticationRequestView(AuthenticationRequestView):
    def __init__(self):
        self.alias = ALIAS
        super().__init__()
