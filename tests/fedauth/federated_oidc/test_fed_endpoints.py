from django.urls import reverse_lazy

from tests.base import BaseApiTestCase
from tests.factories import FederatedProviderFactory


class TestDbProviderAuthEndpoints(BaseApiTestCase):

    def setUp(self):
        username = 'andy@random.com'
        self.provider_fed = FederatedProviderFactory(domain='random.com')
        self.auth_url = reverse_lazy('fed-provider-auth', kwargs={'username': username})

    def test_db_provider_authenticate_redirect(self):
        resp = self.get(self.auth_url)
        assert resp.status_code == 302  # redirect
        assert resp.url.startswith(self.provider_fed.auth_endpoint)
