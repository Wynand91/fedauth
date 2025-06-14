from cryptography.fernet import Fernet
from django.conf import settings


SIGN_ALGOS = [
    ('HS256', 'HS256'),
    ('RS256', 'RS256'),
    ('ES256', 'ES256'),
]


def encrypt(plain_text: bytes, key: str | bytes = None) -> bytes:
    """
    Encrypt plain text.
    :param plain_text: text to encrypt
    :param key: key used for encryption
    :return: encrypted ciphertext
    """
    if key is None:
        key = settings.SECRET_KEY
    fernet = Fernet(key)
    return fernet.encrypt(plain_text)


def decrypt(ciphertext: bytes, key: str | bytes = None) -> bytes:
    """
    Decrypt encrypted plain text.
    :param ciphertext: encrypted data
    :param key: key used for encryption
    :return: decrypted plain text
    """
    if key is None:
        key = settings.SECRET_KEY
    fernet = Fernet(key)

    # Ensure ciphertext is bytes
    if isinstance(ciphertext, memoryview):
        ciphertext = ciphertext.tobytes()

    return fernet.decrypt(ciphertext)
