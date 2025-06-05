from fedauth.generic_oidc.views import GenericAuthenticationRequestView

ALIAS = 'jumpcloud'


class JumpcloudAuthenticationRequestView(GenericAuthenticationRequestView):
    def __init__(self):
        self.alias = ALIAS
        super().__init__()
