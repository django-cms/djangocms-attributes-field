# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from jsonfield.forms import JSONFormField

from .widgets import AttributesWidget


class AttributesFormField(JSONFormField):

    def __init__(self, *args, **kwargs):
        if 'widget' not in kwargs:
            kwargs['widget'] = AttributesWidget
        super(AttributesFormField, self).__init__(*args, **kwargs)
