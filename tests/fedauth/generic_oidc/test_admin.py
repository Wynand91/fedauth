# from django.test import TestCase
# from django.contrib.admin.sites import AdminSite
# from django.contrib.auth import get_user_model
# from django.urls import reverse
#
# from fedauth.federated_oidc.admin import FederatedProviderAdmin
# from fedauth.federated_oidc.models import FederatedProvider
# from fedauth.crypto import decrypt
# from tests.base import FakeRequest
# from tests.factories import FederatedProviderFactory
#
#
# class TestFederatedProviderAdmin(TestCase):
#
#     def setUp(self):
#         self.superuser = get_user_model().objects.create(
#             username='admin',
#             is_superuser=True,
#             is_staff=True,
#         )
#         self.client.force_login(self.superuser)
#         self.admin = FederatedProviderAdmin(FederatedProvider, AdminSite())
#         self.fp = FederatedProviderFactory()
#
#     def test_get_fields(self):
#         # client_secret should not be included for read fields (object exists)
#         assert 'client_secret' not in self.admin.get_fields(FakeRequest, self.fp)
#
#         # client should be included for write (no object yet)
#         assert 'client_secret' in self.admin.get_fields(FakeRequest, None)
#
#     def test_create_fp_object_failure(self):
#         self.url = reverse('admin:federated_providers_federatedprovider_add')
#         resp = self.client.post(self.url, {})
#         assert resp.status_code == 200
#         assert ['This field is required.'] in resp.context_data['errors']
#
#     def test_create_fp_save(self):
#         domain = 'test.com'
#         client_secret = 'KFcP.k4GmTqCv2.9HtB3Dp2~3q'
#         self.url = reverse('admin:federated_providers_federatedprovider_add')
#         resp = self.client.post(self.url, {
#             'domain': domain,
#             'auth_endpoint': 'https://some.ip.com/auth/',
#             'token_endpoint': 'https://some.ip.com/token/',
#             'user_endpoint': 'https://some.ip.com/user/',
#             'jwks_endpoint': 'https://some.ip.com/keys/',
#             'client_id': 'c9e1ee6c-9755-9755-ac86-5e7b657f4d53',
#             'client_secret': client_secret,
#             'sign_algo': 'RS256',
#             'scopes': "openid profile email phone groups",
#         })
#         assert resp.status_code == 302
#         new_fp = FederatedProvider.objects.get(domain=domain)
#         # check that client secret is saved and encrypted
#         encrypted_secret = new_fp.client_secret_cipher
#         assert decrypt(encrypted_secret).decode() == client_secret
