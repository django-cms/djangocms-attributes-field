import os

from django.apps import apps
from django.forms import Media, Widget
from django.forms.utils import flatatt
from django.utils.html import escape, mark_safe, strip_spaces_between_tags
from django.utils.translation import gettext as _

# NOTE: Inlining the CSS and JS code allows avoiding to register
# djangocms_attributes_field in INSTALLED_APPS. It will, however,
# potentially conflict with a CSP.
# If "djangocms_attributes_field" is installed, then the media class
# of the widget is used, otherwise the CSS and JS is inlined by reading from
# file system at startup. This way, we support CSPs that do not allow
# inline scripts/styles, but also support projects that historically do not use
# djangocms_attributes_field as an app, but still want to use the widget.
_inline_code = None

def _read_inline_code():
    if apps.is_installed('djangocms_attributes_field'):
        _inline_code = ""
    else:
        def _read_static_files():
            base_dir = os.path.dirname(os.path.abspath(__file__))
            with open(os.path.join(base_dir, 'static/djangocms_attributes_field/widget.js'), 'r', encoding='utf-8') as f:
                js_code = f.read()
            with open(os.path.join(base_dir, 'static/djangocms_attributes_field/widget.css'), 'r', encoding='utf-8') as f:
                css_code = f.read()
            return css_code, js_code

        _inline_code = "<style>{}</style><script>{}</script>".format(*_read_static_files())
    return _inline_code


class AttributesWidget(Widget):
    """
    A widget that displays key/value pairs from JSON as a list of text input
    box pairs and back again.
    """
    # Heavily modified from a code snippet by Huy Nguyen:
    # https://www.huyng.com/posts/django-custom-form-widget-for-dictionary-and-tuple-key-value-pairs
    def __init__(self, *args, **kwargs):
        """
        Supports additional kwargs: `key_attr`, `val_attr`, `sorted`.
        """
        self.key_attrs = kwargs.pop('key_attrs', {})
        self.val_attrs = kwargs.pop('val_attrs', {})
        self.sorted = sorted if kwargs.pop('sorted', True) else lambda x: x
        super().__init__(*args, **kwargs)

    @property
    def media(self):
        """
        Returns the media required by this widget.
        If djangocms_attributes_field is installed, it will use the media class
        of the widget, otherwise it will inline the CSS and JS.
        """

        global _inline_code

        if _inline_code is None:
            _inline_code = _read_inline_code()

        if _inline_code:
            return Media()
        else:
            return Media(
                css={
                    'all': ('djangocms_attributes_field/widget.css',)
                },
                js=(
                    'djangocms_attributes_field/widget.js',
                )
            )

    def _render_row(self, key, value, field_name, key_attrs, val_attrs):
        """
        Renders to HTML a single key/value pair row.

        :param key: (str) key
        :param value: (str) value
        :param field_name: (str) String name of this field
        :param key_attrs: (dict) HTML attributes to be applied to the key input
        :param val_attrs: (dict) HTML attributes to be applied to the value input
        """
        template = """
        <div class="form-row attributes-pair">
            <div class="field-box">
               <input type="text" class="attributes-key" name="attributes_key[{field_name}]" value="{key}" {key_attrs}>
            </div>
            <div class="field-box">
               <input type="text" class="attributes-value"
                      name="attributes_value[{field_name}]"
                      value="{value}" {val_attrs}>
                <a class="delete-attributes-pair deletelink" href="#" title="{remove}"></a>
            </div>
        </div>
        """.format(
            key=escape(key),
            value=escape(value),
            field_name=field_name,
            key_attrs=key_attrs,
            val_attrs=val_attrs,
            remove=_('Remove'),
        )

        return strip_spaces_between_tags(template.strip())

    def render(self, name, value, attrs=None, renderer=None):
        """
        Renders this field into an HTML string.

        :param name: (str) name of the field
        :param value: (str) a json string of a two-tuple list automatically passed in by django
        :param attrs: (dict) automatically passed in by django (unused by this function)
        :param renderer: (object) automatically passed in by django (unused by this function)
        """
        if not value:
            value = '{}'

        if attrs is None:
            attrs = {}

        output = '<div class="djangocms-attributes-field">'
        if value and isinstance(value, dict) and len(value) > 0:
            for key in self.sorted(value):
                output += self._render_row(key, value[key], name, flatatt(self.key_attrs), flatatt(self.val_attrs))

        # Add empty template
        output += """
        <div class="template hidden">{}
        </div>""".format(self._render_row('', '', name, flatatt(self.key_attrs), flatatt(self.val_attrs)))

        # Add "+" button
        output += """
        <div class="related-widget-wrapper">
            <a class="add-attributes-pair addlink" href="#" title="{title}"></a>
        </div>
        """.format(
            title=_('Add another key/value pair'),
        )
        output += f'</div>{_inline_code}'
        return mark_safe(output)

    def value_from_datadict(self, data, files, name):
        """
        Returns the dict-representation of the key-value pairs
        sent in the POST parameters

        :param data: (dict) request.POST or request.GET parameters.
        :param files: (list) request.FILES
        :param name: (str) the name of the field associated with this widget.
        """
        key_field = f'attributes_key[{name}]'
        val_field = f'attributes_value[{name}]'
        if key_field in data and val_field in data:
            keys = data.getlist(key_field)
            values = data.getlist(val_field)
            return dict([item for item in zip(keys, values) if not item[0] == ''])
        return {}

    def value_omitted_from_data(self, data, files, name):
        return False
