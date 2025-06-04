from django.db import models

from fedauth.models import BaseProvider


class FederatedProvider(BaseProvider):
    """
    This model stores all the federated domain provider settings (e.g. 'company.com')
    """
    domain = models.CharField(max_length=48, unique=True)
