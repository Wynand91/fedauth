from django.urls import reverse_lazy

from tests.base import BaseApiTestCase
from tests.factories import FederatedProviderFactory


class TestAdminLoginView(BaseApiTestCase):

    def setUp(self):
        self.username = 'wynand@byteorbit.com'
        self.provider = FederatedProviderFactory(domain='byteorbit.com')
        self.auth_url = reverse_lazy('admin-login')

    def test_admin_with_federated_username(self):
        resp = self.post(self.auth_url, data={'username': self.username})
        # redirect to 'fed-provider-auth' endpoint with username as kwarg
        assert resp.status_code == 302
        assert resp.url == reverse_lazy('fed-provider-auth', kwargs={'username': self.username})

    def test_admin_with_non_federated_username(self):
        non_federated_username = 'john@gmail.com'
        resp = self.post(self.auth_url, data={'username': non_federated_username})
        # redirect to 'default-admin-login' endpoint with username as kwarg - kwarg is used to pre-populate next form
        assert resp.status_code == 302
        assert resp.url == reverse_lazy('default-admin-login', kwargs={'username': non_federated_username})


class TestAdminDefaultLoginView(BaseApiTestCase):

    def test_admin_default_admin_login(self):
        username = 'john@gmail.com'
        url = reverse_lazy('default-admin-login', kwargs={'username': username})
        resp = self.get(url)
        assert resp.status_code == 200
        # check that username is pre-populated into form
        assert resp.context_data['form'].initial['username'] == username
        assert username in str(resp.content)
