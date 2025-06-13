from fedauth.static_oidc.views import StaticAuthenticationRequestView

ALIAS = 'jumpcloud'


class JumpcloudAuthenticationRequestView(StaticAuthenticationRequestView):
    def __init__(self):
        self.alias = ALIAS
        super().__init__()
