from urllib.request import Request

from rest_framework.test import APIClient, APITestCase


class BaseApiTestCase(APITestCase):
    client: APIClient

    def get(self, url: str):
        return self.client.get(url)

    def post(self, url: str, data: dict = None):
        return self.client.post(url, data)


class FakeRequest(Request):
    """
    fake request that mocks real request. We only need user, session and GET attributes for tests.
    """
    user = None
    session = {}
    GET = {}


class FakeToken:
    access_token = 'access'

    def __str__(self) -> str:
        return 'refresh'
