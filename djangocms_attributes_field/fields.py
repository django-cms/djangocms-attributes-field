# -*- coding: utf-8 -*-

from __future__ import unicode_literals

import json
import jsonfield
import re

from jsonfield.forms import JSONFormField

from django.core.validators import RegexValidator
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext as _

from .widgets import AttributesWidget


regex_key_validator = RegexValidator(regex=r'^[a-z][-a-z0-9_]*\Z',
                                     flags=re.IGNORECASE, code='invalid')


class AttributesFormField(JSONFormField):
    """
    Sub-classed to set the default widget to AttributesWidget.
    """
    def __init__(self, *args, **kwargs):
        kwargs.setdefault('widget', AttributesWidget)
        super(AttributesFormField, self).__init__(*args, **kwargs)


class AttributesField(jsonfield.JSONField):
    """
    This is an opinionated sub-class of JSONField. Here's a summary of the
    primary differences:

        * Instead of storing any arbitrary JSON, we stick to a flat list of
          key/value pairs;
        * Keys must start with a letter and only contain letters, numbers,
          underscores and hyphens;
        * We accept a field parameter `excluded_keys` which contains a list
          of keys we do not accept and enforce this;
        * Validation checks for both key format and excluded_keys are done
          in a case-insensitive manner;
        * The default widget is AttributesWidget from this package.
    """
    def __init__(self, *args, **kwargs):
        excluded_keys = kwargs.pop('excluded_keys', [])
        # Note we accept uppercase letters in the param, but the comparison
        # is not case sensitive. So, we coerce the input to lowercase here.
        self.excluded_keys = [key.lower() for key in excluded_keys]
        super(AttributesField, self).__init__(*args, **kwargs)

    def validate(self, value, model_instance):
        super(AttributesField, self).validate(value, model_instance)
        for key, val in value.items():
            self.validate_key(key)
            self.validate_value(key, val)

    def validate_key(self, key):
        """
        A key must start with a letter, but can otherwise contain letters,
        numbers, dashes or underscores. It must not also be part of
        `excluded_keys` as configured in the field.

        :param key: (str) The key to validate
        """
        # Verify the key is not one of `excluded_keys`.
        if key.lower() in self.excluded_keys:
            raise ValidationError(
                _('"{key}" is excluded by configuration and cannot be used as '
                  'a key.').format(key=key))
        # Also check that it fits our permitted syntax
        try:
            regex_key_validator(key)
        except ValidationError:
            # Seems silly to catch one then raise another ValidationError, but
            # the RegExValidator doesn't use placeholders in its error message.
            raise ValidationError(
                _('"{key}" is not a valid key. Keys must start with at least '
                  'one letter and consist only of the letters, numbers, '
                  'underscores or hyphens.').format(key=key))

    def validate_value(self, key, value):
        """
        A value can be anything that can be JSON-ified.

        :param key: (str) The key of the value
        :param value: (str) The value to validate
        """
        try:
            json.dumps(value)
        except (TypeError, ValueError):
            raise ValidationError(
                _('The value for the key "{key}" is invalid. Please enter a '
                  'value that can be represented in JSON.').format(key=key))

    def formfield(self, **kwargs):
        defaults = {
            'form_class': AttributesFormField,
            'widget': AttributesWidget
        }
        defaults.update(**kwargs)
        return super(AttributesField, self).formfield(**defaults)
