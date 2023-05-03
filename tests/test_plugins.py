import warnings

from cms import __version__
from cms.api import add_plugin, create_page
from cms.test_utils.testcases import CMSTestCase

from .test_app.cms_plugins import TestPluginPlugin


# we're testing the plugin generation from a sample django CMS addon in
# tests/test_app
class TestPluginTestCase(CMSTestCase):

    def setUp(self):
        self.language = "en"
        self.page = create_page(
            title="page",
            template="page.html",
            language=self.language,
        )
        if __version__ < "4":
            self.page.publish(self.language)
            self.placeholder = self.page.placeholders.get(slot="content")
        else:
            self.placeholder = self.page.get_placeholders(self.language).get(slot="content")
        self.superuser = self.get_superuser()

    def tearDown(self):
        self.page.delete()
        self.superuser.delete()

    def test_plugin_rendering(self):
        request_url = self.page.get_absolute_url(self.language) + "?toolbar_off=true"
        add_plugin(
            placeholder=self.placeholder,
            plugin_type=TestPluginPlugin.__name__,
            language=self.language,
            attributes1={"data-tracking": "google"},
            attributes2={"class": "some new classes"},
        )
        if __version__ < "4":
            self.page.publish(self.language)

        with self.login_user_context(self.superuser):
            response = self.client.get(request_url)

        self.assertContains(response, "data-tracking")
        self.assertContains(response, "google")
        self.assertContains(response, "class")
        self.assertContains(response, "some new classes")

    def test_plugin_form(self):
        request_url = self.get_add_plugin_uri(
            placeholder=self.placeholder,
            plugin_type=TestPluginPlugin.__name__,
            language=self.language,
        )

        data = {
            "label": "test",
            "attributes_key[attributes1]": "data-tracking",
            "attributes_value[attributes1]": "google",
            "attributes_key[attributes2]": "class",
            "attributes_value[attributes2]": "some new classes"
        }

        # test actual form rendering
        with self.login_user_context(self.superuser), warnings.catch_warnings():
            # hide the "DontUsePageAttributeWarning" warning when using
            # `get_add_plugin_uri` to get cleaner test results
            warnings.simplefilter("ignore")
            response = self.client.post(request_url, data)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, '<div class="success">')

        # test error for excluded keys
        data = {
            "label": "test",
            "attributes_key[attributes2]": "style",
            "attributes_value[attributes2]": "this fails"
        }

        # test actual form rendering
        with self.login_user_context(self.superuser), warnings.catch_warnings():
            # hide the "DontUsePageAttributeWarning" warning when using
            # `get_add_plugin_uri` to get cleaner test results
            warnings.simplefilter("ignore")
            response = self.client.post(request_url, data)

        self.assertContains(
            response,
            "&quot;style&quot; is excluded by configuration and cannot be "
            "used as a key.",
        )

        # test error if an invalid option is probided
        data = {
            "label": "test",
            "attributes_key[attributes2]": "data test",
            "attributes_value[attributes2]": "hello world"
        }

        # test actual form rendering
        with self.login_user_context(self.superuser), warnings.catch_warnings():
            # hide the "DontUsePageAttributeWarning" warning when using
            # `get_add_plugin_uri` to get cleaner test results
            warnings.simplefilter("ignore")
            response = self.client.post(request_url, data)

        self.assertContains(
            response,
            "&quot;data test&quot; is not a valid key. Keys must start with "
            "at least one letter and consist only of the letters, numbers, "
            "underscores or hyphens.",
        )
