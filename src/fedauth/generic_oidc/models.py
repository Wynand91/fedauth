from django.db import models

from fedauth.models import BaseProvider


class GenericProvider(BaseProvider):
    """
    This model stores all the generic provider settings (for non-federated login - e.g. login with facebook etc)
    """
    provider = models.CharField(max_length=48, unique=True)
