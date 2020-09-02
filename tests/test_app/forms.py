from django import forms

from djangocms_attributes_field.widgets import AttributesWidget

from .models import TestPlugin


class TestPluginForm(forms.ModelForm):
    class Meta:
        model = TestPlugin
        fields = ['attributes1', 'attributes2']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['attributes2'].widget = AttributesWidget(
            key_attrs={'style': 'width:250px'},
            val_attrs={'style': 'width:500px'},
        )
