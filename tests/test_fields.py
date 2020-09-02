from django.core.exceptions import ValidationError
from django.db.models.fields import NOT_PROVIDED
from django.test.testcases import TestCase

from djangocms_attributes_field.fields import (
    AttributesField, AttributesFormField,
)


class Noop:
    pass


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


class AttributesFieldsTestCase(TestCase):

    def test_attributes_form_field(self):
        field = AttributesFormField()
        # to_python method
        self.assertEquals(field.to_python({"test": True}), {"test": True})
        with self.assertRaises(ValidationError):
            field.to_python("no json")
        # validate method
        field.validate({})
        field.required = True
        with self.assertRaises(ValidationError):
            field.validate(None)

    def test_attributes_field(self):
        field = AttributesField(null=True, default={"my": "default"})
        # formfield method
        self.assertEquals(field.formfield().initial, {"my": "default"})
        # from_db_value method
        self.assertIsNone(field.from_db_value(None))
        self.assertEquals(
            field.from_db_value('{"test": "test"}'),
            {"test": "test"},
        )
        self.assertEquals(
            field.from_db_value({"test": "test"}),
            {"test": "test"},
        )
        # get_db_prep_value method
        self.assertIsNone(field.get_db_prep_value(None))
        field.null = False
        field.blank = True
        self.assertEquals(field.get_db_prep_value(None), "")
        # get_default method
        field = AttributesField(default='{"my": "default"}')
        field.default = NOT_PROVIDED
        field.get_default()
        # get_internal_type method
        self.assertEquals(field.get_internal_type(), "TextField")
        # validate method
        with self.assertRaises(ValidationError):
            field.validate(None, Noop)
