# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.contrib.staticfiles.templatetags.staticfiles import static
from django.forms import Widget
from django.forms.widgets import flatatt
from django.utils.html import escape
from django.utils.text import mark_safe
from django.utils.translation import ugettext as _


class AttributesWidget(Widget):
    """
    A widget that displays key/value pairs from JSON as a list of text input
    box pairs and back again.
    """
    # Heavily modified from a code snippet by Huy Nguyen:
    # https://www.huyng.com/posts/django-custom-form-widget-for-dictionary-and-tuple-key-value-pairs
    def __init__(self, *args, **kwargs):
        """
        Supports additional kwargs: `key_attr` and `val_attr`.
        """
        self.key_attrs = kwargs.pop('key_attrs', {})
        self.val_attrs = kwargs.pop('val_attrs', {})
        super(AttributesWidget, self).__init__(*args, **kwargs)

    def _render_row(self, key, value, field_name, key_attrs, val_attrs):
        """
        Renders to HTML a single key/value pair row.

        :param key: (str) key
        :param value: (str) value
        :param field_name: (str) String name of this field
        :param key_attrs: (dict) HTML attributes to be applied to the key input
        :param val_attrs: (dict) HTML attributes to be applied to the value input
        """
        return """
        <div class="form-row attributes-pair">
            <div class="field-box">
               <label>Key</label>
               <input type="text" class="attributes-key" name="attributes_key[{field_name}]" value="{key}" {key_attrs}>
            </div>
            <div class="field-box">
               <label>Value</label>
               <input type="text" class="attributes-value"
                      name="attributes_value[{field_name}]"
                      value="{value}" {val_attrs}>
                <a class="delete-attributes-pair" href="#" title="{remove}">
                    <img src="{deleteIconSrc}" alt="{remove}">
                </a>
            </div>
        </div>
        """.format(
            key=escape(key),
            value=escape(value),
            field_name=field_name,
            key_attrs=key_attrs,
            val_attrs=val_attrs,
            remove=_('Remove'),
            deleteIconSrc=static('admin/img/icon-deletelink.svg'),
        )

    def render(self, name, value, attrs=None):
        """
        Renders this field into an HTML string.

        :param name: (str) name of the field
        :param value: (str) a json string of a two-tuple list automatically passed in by django
        :param attrs: (dict) automatically passed in by django (unused by this function)
        """
        if not value:
            value = '{}'

        if attrs is None:
            attrs = {}

        output = '<div class="djangocms-attributes-field">'
        if value and isinstance(value, dict) and len(value) > 0:
            for key in sorted(value):
                output += self._render_row(key, value[key], name, flatatt(self.key_attrs), flatatt(self.val_attrs))

        # Add empty template
        output += """
        <div class="template hidden">{0}
        </div>""".format(self._render_row('', '', name, flatatt(self.key_attrs), flatatt(self.val_attrs)))

        # Add "+" button
        output += """
        <div class="related-widget-wrapper">
            <a class="add-attributes-pair" href="#" title="{title}">
                <img src="{addIconSrc}" alt="{title}">
            </a>
        </div>
        """.format(
            title=_('Add another key/value pair'),
            addIconSrc=static('admin/img/icon-addlink.svg'),
        )
        output += '</div>'

        # NOTE: This is very consciously being inlined into the HTML because
        # if we use the Django "class Media()" mechanism to include this JS
        # behaviour, then every project that uses any package that uses Django
        # CMS Attributes Field will also have to add this package to its
        # INSTALLED_APPS. By inlining the JS and CSS here, we avoid this.
        output += """
        <style>
            .delete-attributes-pair,
            .add-attributes-pair {
                border: 1px solid #ddd;
                border-radius: 3px;
                display: inline-block;
                padding: 6px 10px 8px;
            }
            .delete-attributes-pair {
                margin-left: 16px;
            }
        </style>
        <script>
            (function ($) {
                function fixUpIds (fieldGroup) {
                    fieldGroup.find('.attributes-pair').each(function (idx, value) {
                        $(value).find('.attributes-key').attr('id', 'field-key-row-' + idx)
                                .siblings('label').attr('for', 'field-key-row-' + idx);
                        $(value).find('.attributes-value').attr('id', 'field-value-row-' + idx)
                                .siblings('label').attr('for', 'field-value-row-' + idx);
                    });
                }

                $(document).ready(function () {
                    $('.djangocms-attributes-field').each(function () {
                        var that = $(this);
                        var emptyRow = that.find('.template');
                        var btnAdd = that.find('.add-attributes-pair');
                        var btnDelete = that.find('.delete-attributes-pair');

                        btnAdd.on('click', function (event) {
                            event.preventDefault();
                            emptyRow.before(emptyRow.find('.attributes-pair').clone());
                            fixUpIds(that);
                        });

                        btnDelete.on('click', function (event) {
                            event.preventDefault();
                            $(this).parents('.attributes-pair').remove();
                            fixUpIds(that);
                        });

                        fixUpIds(that);
                    });
                });
            }(django.jQuery));
        </script>
        """
        return mark_safe(output)

    def value_from_datadict(self, data, files, name):
        """
        Returns the dict-representation of the key-value pairs
        sent in the POST parameters

        :param data: (dict) request.POST or request.GET parameters.
        :param files: (list) request.FILES
        :param name: (str) the name of the field associated with this widget.
        """
        key_field = 'attributes_key[{0}]'.format(name)
        val_field = 'attributes_value[{0}]'.format(name)
        if key_field in data and val_field in data:
            keys = data.getlist(key_field)
            values = data.getlist(val_field)
            return dict([item for item in zip(keys, values) if not item[0] == ''])
        return {}
