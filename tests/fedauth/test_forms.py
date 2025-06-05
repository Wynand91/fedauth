from django.test import TestCase

from fedauth.oidc_admin.forms import UsernameForm


class TestUsernameForm(TestCase):

    def test_form_init(self):
        # check that only username field present.
        form = UsernameForm()
        assert form.fields.get('username')
        assert not form.fields.get('password')
