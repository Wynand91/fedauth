from django.db import models

from fedauth.federated_providers.utils import decrypt, encrypt

from fedauth.models import TimeStampedModel

ALGOS = [
    ('RS256', 'RS256'),
    ('ES256', 'ES256'),
    ('HS256', 'HS256'),
]


class FederatedProvider(TimeStampedModel):
    auth_endpoint = models.URLField()
    token_endpoint = models.URLField()
    user_endpoint = models.URLField()
    jwks_endpoint = models.URLField()
    domain = models.CharField(max_length=48, unique=True)
    client_id = models.CharField(max_length=48)
    client_secret_cipher = models.BinaryField()
    sign_algo = models.CharField(max_length=5, choices=ALGOS, default='RS256')
    scopes = models.CharField(max_length=250, default="openid profile email phone groups")  # IP configured scopes
    objects = models.Manager()

    def get_client_secret(self) -> str:
        return decrypt(self.client_secret_cipher).decode()

    def set_client_secret(self, client_secret: str):
        self.client_secret_cipher = encrypt(client_secret.encode())

    client_secret = property(get_client_secret, set_client_secret)  # noqa
