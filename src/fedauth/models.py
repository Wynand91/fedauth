from django.db import models

from fedauth.crypto import decrypt, encrypt


class TimeStampedModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class BaseProvider(TimeStampedModel):
    auth_endpoint = models.URLField()
    token_endpoint = models.URLField()
    user_endpoint = models.URLField()
    jwks_endpoint = models.URLField()
    client_id = models.CharField(max_length=48)
    client_secret_cipher = models.BinaryField()
    sign_algo = models.CharField(max_length=5, choices=SIGN_ALGOS, default='RS256')
    scopes = models.CharField(max_length=250, default="openid profile email phone groups")  # IP configured scopes
    objects = models.Manager()

    class Meta:
        abstract = True

    def get_client_secret(self) -> str:
        return decrypt(self.client_secret_cipher).decode()

    def set_client_secret(self, client_secret: str):
        self.client_secret_cipher = encrypt(client_secret.encode())

    client_secret = property(get_client_secret, set_client_secret)  # noqa
