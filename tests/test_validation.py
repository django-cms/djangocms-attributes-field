# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.core.exceptions import ValidationError
from django.test.testcases import TestCase

from djangocms_attributes_field.fields import AttributesField


class KeyValidationTests(TestCase):

    def test_validate_key(self):
        field = AttributesField()
        # Normal, expected patterns
        try:
            field.validate_key('target')
            field.validate_key('a')
            field.validate_key('A')
            field.validate_key('a1')
            field.validate_key('A1')
            field.validate_key('a-1')
            field.validate_key('a_1')
            field.validate_key('a-A1_')
        except ValidationError:
            self.fail('Keys that pass have failed.')

        # We don't accept these though...
        with self.assertRaises(ValidationError):
            field.validate_key('-abc')
        with self.assertRaises(ValidationError):
            field.validate_key('_abc')
        with self.assertRaises(ValidationError):
            field.validate_key('31-flavors')
        with self.assertRaises(ValidationError):
            field.validate_key('__init__')
        with self.assertRaises(ValidationError):
            field.validate_key('cöordinate')
        with self.assertRaises(ValidationError):
            field.validate_key('<tag>')
        with self.assertRaises(ValidationError):
            field.validate_key('#hash')

    def test_excluded_keys(self):
        # First prove that the keys we're about to test would normally pass
        field = AttributesField()
        try:
            field.validate_key('href')
            field.validate_key('src')
        except ValidationError:
            self.fail('Keys that pass have failed.')

        # Now show that they no longer pass if explicitly exclude
        field = AttributesField(excluded_keys=['href', 'src', ])

        with self.assertRaises(ValidationError):
            field.validate_key('href')
        with self.assertRaises(ValidationError):
            field.validate_key('src')
