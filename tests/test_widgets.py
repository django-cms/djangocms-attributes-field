from django.test import override_settings
from django.test.testcases import TestCase

from djangocms_attributes_field.widgets import AttributesWidget


class AttributesWidgetsTestCase(TestCase):

    def test_widget(self):
        widget = AttributesWidget()
        row = widget._render_row("test", "test", "test", "test", "test")
        # _render_row
        self.assertIn("attributes_key[test]", row)
        self.assertIn("attributes_value[test]", row)
        # render
        widget.render("name", None)
        widget.render("name", None, attrs="test")
        widget.render("name", {"test": "test"})
        # value_from_datadict
        widget.value_from_datadict("", "", None)
        widget.value_omitted_from_data(None, None, None)

    def test_media_property(self):
        from djangocms_attributes_field.widgets import _inline_code

        widget = AttributesWidget()
        media = widget.media
        self.assertIn('djangocms_attributes_field/widget.css', media._css['all'])
        self.assertIn('djangocms_attributes_field/widget.js', media._js)
        # Test inline code
        self.assertEqual(_inline_code, "")

    @override_settings(
        INSTALLED_APPS=[]
    )
    def test_media_property_with_inline_code(self):
        from djangocms_attributes_field import widgets

        # Set inline code to a non-empty value
        widgets._inline_code = None  # Reset cache

        widget = AttributesWidget()
        media = widget.media
        self.assertEqual(media._css, {})
        self.assertEqual(media._js, [])
        # Reset inline code for other tests
        self.assertIn("<script>", widgets._inline_code)
        self.assertIn("<style>", widgets._inline_code)
