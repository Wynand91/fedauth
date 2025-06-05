from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.test import TestCase

from fedauth.federated_oidc.models import FederatedProvider
from fedauth.generic_oidc.models import GenericProvider
from fedauth.utils import get_federated_provider_settings, get_non_federated_provider_settings
from tests.factories import FederatedProviderFactory, GenericProviderFactory


class TestUtils(TestCase):

    def setUp(self):
        self.fp: FederatedProvider = FederatedProviderFactory()
        self.gp: GenericProvider = GenericProviderFactory()
        self.domain = self.fp.domain
        self.alias = self.gp.provider

    def test_get_federated_provider_settings(self):
        # model setting
        algo_config = get_federated_provider_settings('OIDC_RP_SIGN_ALGO', self.domain)
        assert algo_config == self.fp.sign_algo

        # global setting (not found on model)
        callback_config = get_federated_provider_settings('OIDC_AUTHENTICATION_CALLBACK_URL', self.domain)
        assert callback_config == getattr(settings, 'OIDC_AUTHENTICATION_CALLBACK_URL')

    def test_get_non_federated_provider_settings(self):
        # model setting
        client_id_config = get_non_federated_provider_settings('OIDC_RP_CLIENT_ID', self.alias)
        assert client_id_config == self.gp.client_id

        # global settings (not stored on model)
        callback_config = get_non_federated_provider_settings('OIDC_AUTHENTICATION_CALLBACK_URL', self.alias)
        assert callback_config == getattr(settings, 'OIDC_AUTHENTICATION_CALLBACK_URL')

    def test_get_settings_default(self):
        # setting not a global setting, or on provider settings, so use default if passed as arg
        config = get_non_federated_provider_settings('FAKE_SETTINGS', self.alias, 'hello')
        assert config == 'hello'

    def test_get_settings_not_exist(self):
        # if settings can't be found on model, on setting config, and no default arg, throw error.
        with self.assertRaises(ImproperlyConfigured) as exc:
            get_non_federated_provider_settings('MADE_UP_SETTING', self.alias)
        assert str(exc.exception) == 'Setting MADE_UP_SETTING not found'

