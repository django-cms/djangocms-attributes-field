from cms.plugin_base import CMSPluginBase
from cms.plugin_pool import plugin_pool

from .forms import TestPluginForm
from .models import TestPlugin


class TestPluginPlugin(CMSPluginBase):
    model = TestPlugin
    form = TestPluginForm
    name = "Test plugin"
    render_template = 'test_app/test.html'


plugin_pool.register_plugin(TestPluginPlugin)
