from django.test import TestCase

from cryptography.fernet import Fernet

from fedauth.crypto import encrypt, decrypt


class TestUtils(TestCase):

    def setUp(self):
        self.secret = 'HWcI.p6WmTqCv6.OHtG3Dp0~Ep'
        self.key = Fernet.generate_key()

    def test_crypto(self):
        encrypted_secret = encrypt(self.secret.encode(), self.key)
        decrypted_secret = decrypt(encrypted_secret, self.key)
        assert decrypted_secret.decode() == self.secret
