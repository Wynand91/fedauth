import logging

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError, ImproperlyConfigured
from mozilla_django_oidc.auth import OIDCAuthenticationBackend as DefaultOidcAuthBackend

from fedauth.mixins import AuthBackendSettingsMixin
from fedauth.validators import PhoneNumberValidator, validate_phone

LOGGER = logging.getLogger(__name__)

UserModel = get_user_model()


class OIDCAuthenticationBackend(AuthBackendSettingsMixin, DefaultOidcAuthBackend):
    """
    During the OIDC callback view handling, the authenticate() method is called, which will cycle through authentication
    backends defined in the settings. It will then use this class create/update and authenticate the user.
    """
    domain = None
    provider = None
    request = None

    def __init__(self, *args, **kwargs):
        # Don't call super '__init__' here, as it tries to set class variables before
        # username kwarg is available. Settings will be obtained later when 'authenticate' method runs.
        self.UserModel = get_user_model()

    def configure_oidc_settings(self):
        """
        Because this step is skipped in super init call, we set attributes here, when the username kwarg is available.
        """
        self.OIDC_OP_TOKEN_ENDPOINT = self.get_settings("OIDC_OP_TOKEN_ENDPOINT")
        self.OIDC_OP_USER_ENDPOINT = self.get_settings("OIDC_OP_USER_ENDPOINT")
        self.OIDC_OP_JWKS_ENDPOINT = self.get_settings("OIDC_OP_JWKS_ENDPOINT", None)
        self.OIDC_RP_CLIENT_ID = self.get_settings("OIDC_RP_CLIENT_ID")
        self.OIDC_RP_CLIENT_SECRET = self.get_settings("OIDC_RP_CLIENT_SECRET")
        self.OIDC_RP_SIGN_ALGO = self.get_settings("OIDC_RP_SIGN_ALGO", "HS256")
        self.OIDC_RP_IDP_SIGN_KEY = self.get_settings("OIDC_RP_IDP_SIGN_KEY", None)

        if (
                self.OIDC_RP_SIGN_ALGO.startswith("RS") or self.OIDC_RP_SIGN_ALGO.startswith("ES")
        ) and (
                self.OIDC_RP_IDP_SIGN_KEY is None and self.OIDC_OP_JWKS_ENDPOINT is None
        ):
            msg = "{} alg requires OIDC_RP_IDP_SIGN_KEY or OIDC_OP_JWKS_ENDPOINT to be configured."
            raise ImproperlyConfigured(msg.format(self.OIDC_RP_SIGN_ALGO))

    def authenticate(self, request, **kwargs):
        """
        We only override this method in order to configure the settings before actual authenticate method runs,
        since the settings initialization was skipped during init.
        """
        self.request = request
        if not self.request:
            return None

        self.configure_oidc_settings()
        return super().authenticate(request, **kwargs)

    def filter_users_by_claims(self, claims):
        # clear session of values that is not needed anymore, since user is already authenticated at this point.
        self.request.session.pop('domain', None)
        self.request.session.pop('provider', None)
        self.request.session.pop('source', None)
        return super().filter_users_by_claims(claims)

    def get_username(self, claims):
        # bypass mozilla's username encryption step. We just need the email.
        return claims['email']

    def create_user(self, claims):
        user: UserModel = super(OIDCAuthenticationBackend, self).create_user(claims)
        return self.update_user(user, claims)

    def update_user(self, user, claims):
        # set user details from claims
        user.first_name = claims.get('given_name', '')
        user.last_name = claims.get('family_name', '')
        user.is_superuser = getattr(settings, "OIDC_SUPER_GROUP") in claims.get("groups", [])
        user.is_staff = getattr(settings, "OIDC_ADMIN_GROUP") in claims.get("groups", [])


        phone_number: str = claims.get('phone_number', '')
        if phone_number and hasattr(UserModel, 'phone'):  # TODO: make phone number field customizable.
            phone_number = phone_number.replace(' ', '')
            try:
                validate_phone(phone_number)
            except ValidationError:
                LOGGER.info(f"Invalid phone number: {phone_number}")
            else:
                user.phone = phone_number

        user.save()
        return user
