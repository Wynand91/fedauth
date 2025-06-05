from django.test import TestCase
from django.core.exceptions import ValidationError

from fedauth.validators import validate_phone



class TestPhoneValidator(TestCase):

    def test_valid_phone_number(self):
        valid_phone = '+278791231234'
        assert validate_phone(valid_phone) == valid_phone

    def test_invalid_phone_number(self):
        invalid_err = "['Invalid phone number. format: +27821234567']"
        with self.assertRaises(ValidationError) as exc:
            validate_phone('')
        assert str(exc.exception) == invalid_err

        with self.assertRaises(ValidationError):
            validate_phone('phonenumber')
        assert str(exc.exception) == invalid_err

        # phone should start with +
        with self.assertRaises(ValidationError) as exc:
            validate_phone('278791231234')
        assert str(exc.exception) == invalid_err
