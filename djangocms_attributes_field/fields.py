# -*- coding: utf-8 -*-

from __future__ import unicode_literals

import json
import re

from django import forms
from django.core.validators import RegexValidator
from django.core.exceptions import ImproperlyConfigured, ValidationError
from django.db import models
from django.utils.functional import curry
from django.utils.html import mark_safe, conditional_escape
from django.utils.translation import ugettext as _, ugettext_lazy
from django.utils import six

from .widgets import AttributesWidget


regex_key_validator = RegexValidator(regex=r'^[a-z][-a-z0-9_]*\Z',
                                     flags=re.IGNORECASE, code='invalid')


class AttributesFormField(forms.CharField):
    empty_values = [None, '']

    def __init__(self, *args, **kwargs):
        kwargs.setdefault('widget', AttributesWidget)
        super(AttributesFormField, self).__init__(*args, **kwargs)

    def to_python(self, value):
        if isinstance(value, six.string_types) and value:
            try:
                return json.loads(value)
            except ValueError as exc:
                raise forms.ValidationError(
                    'JSON decode error: %s' % (six.u(exc.args[0]),)
                )
        else:
            return value

    def validate(self, value):
        # This is required in older django versions.
        if value in self.empty_values and self.required:
            raise forms.ValidationError(self.error_messages['required'], code='required')


class AttributesField(models.Field):
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
    default_error_messages = {
        'invalid': ugettext_lazy("'%s' is not a valid JSON string.")
    }
    description = "JSON object"

    def __init__(self, *args, **kwargs):
        if not kwargs.get('null', False):
            kwargs['default'] = kwargs.get('default', dict)
        excluded_keys = kwargs.pop('excluded_keys', [])
        # Note we accept uppercase letters in the param, but the comparison
        # is not case sensitive. So, we coerce the input to lowercase here.
        self.excluded_keys = [key.lower() for key in excluded_keys]
        super(AttributesField, self).__init__(*args, **kwargs)
        self.validate(self.get_default(), None)

    def formfield(self, **kwargs):
        defaults = {
            'form_class': AttributesFormField,
            'widget': AttributesWidget
        }
        defaults.update(**kwargs)
        return super(AttributesField, self).formfield(**defaults)

    def from_db_value(self, value, expression, connection, context):
        """
        This is a temporary workaround for #7 taken from
        https://bitbucket.org/schinckel/django-jsonfield/pull-requests/32/make-from_db_value-compatible-with/diff
        See there for full discussion
        """
        if value is None:
            return None
        elif isinstance(value, six.string_types):
            return json.loads(value)
        else:
            return value

    def get_db_prep_value(self, value, connection=None, prepared=None):
        return self.get_prep_value(value)

    def get_prep_value(self, value):
        if value is None:
            if not self.null and self.blank:
                return ""
            return None
        return json.dumps(value)

    def get_prep_lookup(self, lookup_type, value):
        if lookup_type in ["exact", "iexact", "in", "isnull"]:
            return value
        if lookup_type in ["contains", "icontains"]:
            if isinstance(value, (list, tuple)):
                raise TypeError("Lookup type %r not supported with argument of %s" % (
                    lookup_type, type(value).__name__
                ))
            if isinstance(value, dict):
                return self.get_prep_value(value)[1:-1]
            return self.get_prep_value(value)
        raise TypeError('Lookup type %r not supported' % lookup_type)

    def get_default(self):
        if self.has_default():
            default = self.default
            if callable(default):
                default = default()
            if isinstance(default, six.string_types):
                return json.loads(default)
            return json.loads(json.dumps(default))
        return super(AttributesField, self).get_default()

    def get_internal_type(self):
        return 'TextField'

    def contribute_to_class(self, cls, name, **kwargs):
        """
        Adds a @property: «name»_str that returns a string representation of
        the attributes ready for inclusion on an HTML element.
        """
        super(AttributesField, self).contribute_to_class(cls, name, **kwargs)
        # Make sure we're not going to clobber something that already exists.
        property_name = '{name}_str'.format(name=name)
        if not hasattr(cls, property_name):
            str_property = curry(self.to_str, field_name=name)
            setattr(cls, property_name, property(str_property))

    def validate(self, value, model_instance):
        if not self.null and value is None:
            raise ValidationError(self.error_messages['null'])
        try:
            self.get_prep_value(value)
        except ValueError:
            raise ValidationError(self.error_messages['invalid'] % value)

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

    def value_to_string(self, obj):
        return self._get_val_from_obj(obj)

    @classmethod
    def to_str(cls, obj, field_name):
        """
        Emits stored attributes as a String suitable for for adding to an
        HTML element and performs an outbound filter of excluded_keys.
        """
        # We are explicitly ignoring keys in `excluded_keys` here. The field
        # itself prevents *new* keys from being created that are configured in the
        # field parameter `excluded_keys`. This utility uses the same
        # configuration to prevent any keys in `excluded_keys` from *existing*
        # objects from being emitted.

        if not hasattr(obj, field_name):
            raise ImproperlyConfigured(
                _('"{field_name}" is not a field of {obj|r}').format(
                    obj=obj, field_name=field_name))

        opts = obj._meta
        field = opts.get_field(field_name)

        if not isinstance(field, cls):
            raise TypeError(
                _('"{field_name}" is not an AttributesField').format(
                    field_name=field_name))

        excluded_keys = field.excluded_keys
        value = getattr(obj, field_name)
        try:
            value_items = value.items()
        except AttributeError:
            value_items = [value]

        attrs = []
        for key, val in value_items:
            if key.lower() not in excluded_keys:
                if val:
                    attrs.append('{key}="{value}"'.format(key=key, value=conditional_escape(val)))
                else:
                    attrs.append('{key}'.format(key=key))
        return mark_safe(" ".join(attrs))
