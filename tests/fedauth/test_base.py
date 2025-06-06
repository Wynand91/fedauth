from django.test import TestCase

from fedauth.base import ViewBase


class SomeView(ViewBase):
    """"""


class TestViewBase(TestCase):

    def test_all_required_methods_not_implemented(self):
        view = SomeView()

        with self.assertRaises(NotImplementedError):
            view.get_improper_config_err('AUTH_URL')

        with self.assertRaises(NotImplementedError):
            view.get_model_config('AUTH_URL')
