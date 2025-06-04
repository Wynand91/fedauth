import re

from django.core.exceptions import ValidationError
from django.core.validators import URLValidator


class PhoneNumberValidator:
    """
    Validate phone numbers.
    Expects E.164 format , starting with  "+". min: 7, max 15 digits
    """

    def __init__(self, error='Invalid phone number'):
        self.error = error
        self.pattern = re.compile(r'^\+\d{7,15}$')

    def parse(self, value):
        if not value or not self.pattern.match(value):
            raise ValueError
        return value

    def __call__(self, value):
        try:
            return self.parse(value)
        except ValueError:
            raise ValidationError(self.error, code='invalid', params={'value': value})
