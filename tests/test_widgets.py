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
