from fedauth.backends import OIDCAuthenticationBackend


class AuthBackendSettings(OIDCAuthenticationBackend):
    alias = None

    def __init__(self, alias):
        self.alias = alias
        super().__init__()
