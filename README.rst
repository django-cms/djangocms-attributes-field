===========================
Django CMS Attributes Field
===========================

.. image:: https://travis-ci.org/divio/djangocms-attributes-field.svg?branch=master
    :target: https://travis-ci.org/divio/djangocms-attributes-field

An opinionated implementation of JSONField for arbitrary HTML
element attributes.


--------
Overview
--------

This project aims to provide a sensible means of storing and managing
arbitrary HTML element attributes for later emitting them into templates.

There are a wide variety of types of attributes and using the "normal" Django
method of adding ModelFields for each on a business model is cumbersome at
best and moreover may require related tables to allow cases where any number
of the same type of attribute should be supported (i.e., data-attributes).
This can contribute to performance problems.

To avoid these pitfalls, this package allows all of these attributes to be
stored together in a single text field in the database as a JSON blob, but
provides a nice widget to provide an intuitive, key/value pair interface
and provide sensible validation of the keys used.

Example
-------

The following is an example render of this field's widget render in the Django admin:
(Note this example is from a django CMS project which uses djangocms-admin-style)

.. image:: imgs/example.png
    :width: 406px
    :align: left
    :height: 388px
    :alt: Example render of this model field's widget in the Django Admin

------------
Installation
------------

To install, simply use: ::

    pip install djangocms-attributes-field

then, in your project's ``INSTALLED_APPS`` (if applicable) add: ::

    # settings.py
    ...
    INSTALLED_APPS = [
        ...,
        djangocms_attributes_field,
        ...,
    ]


-----
Usage
-----

AttributeField
--------------

To use this field in your Models.model: ::

    # models.py
    ...
    from django.db import models
    from djangocms_attributes_field.fields import AttributesField
    ...
    MyCoolModel(models.Model):
        ...
        attributes = AttributesField()

That's it!

There is an optional parameter that can be used when declaring the field: ::

    ``excluded_keys`` : This is a list of strings that will not be accepted as
                        valid keys


property: [field_name]_str
++++++++++++++++++++++++++

``AttributeField`` will also provide a handy property ``[field_name]_str``
that will emit the stored key/value pairs as a string suitable for inclusion
in your template for the target HTML element in question. You can use it
like this: ::

    # models.py
    ...
    MyCoolModel(models.Model):
        ...
        html_attributes = AttributesField()


    # templates/my_cool_project/template.html
    ...
    <a href="..." {{ object.html_attributes_str }}>click me</a>
    ...

(Assuming that ``object`` is a context variable containing a
``MyCoolModel`` instance.)

In addition to nicely encapsulating the boring task of converting key/value
pairs into a string with proper escaping and marking-safe, this property also
ensures that *existing* key/value pairs with keys that have since been added
to the field's ``excluded_keys`` are also not included in the output string.


AttributeWidget
---------------

The ``AttributesWidget`` is already used by default by the ``AttributesField``,
but there may be cases where you'd like to override its usage.

The widget supports two additional parameters: ::

    ``key_attrs`` : A dict of HTML attributes to apply to the key input field
    ``val_attrs`` : A dict of HTML attributes to apply to the value input field

These can be useful, for example, if it is necessary to alter the appearance
of the widget's rendered appearance. Again, for example, let's say we needed
to make the key and value inputs have specific widths. We could do this like
so in our ``ModelForm``: ::

    # forms.py

    from django import forms
    from djangocms_attributes_field.widgets import AttributesWidget

    MyCoolForm(forms.ModelForm):
        class Meta:
            fields = ['attributes', ...]

        def __init__(self, *args, **kwargs):
            super(MyCoolForm, self).__init__(*args, **kwargs)
            self.fields['attributes'].widget = AttributesWidget(key_attrs={'style': 'width:250px'},
                                                                val_attrs={'style': 'width:500px'})

