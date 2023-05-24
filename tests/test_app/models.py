from cms.models import CMSPlugin
from django.db import models

from djangocms_attributes_field.fields import AttributesField


class TestPlugin(CMSPlugin):
    label = models.CharField(
        verbose_name="Test app label",
        max_length=255,
    )
    attributes1 = AttributesField()
    attributes2 = AttributesField(
        excluded_keys=["style", "src"],
    )
