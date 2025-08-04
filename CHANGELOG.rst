=========
Changelog
=========

4.1.0 (2025-07-15)
==================

* Add CSP support (load JS and CSS from static files if installed in INSTALLED_APPS)
* fix: Remove test files from wheel

4.0.0 (2024-11-19)
==================

* Moved validation to from AttributeField to AttributeFormField
* Added djangocms_attributes_fields.fields.default_excluded_keys to include
  keys that can execute javascript
* Added tests for Django 5.0, 5.1
* Dropped support for Django 3.2, 4.0, 4.1
* Dropped support for Python 3.6, 3.7, 3.8

3.0.0 (2023-05-24)
==================

* Added tests for Django 4.0, 4.1, 4.2
* Added tests for Python 3.10, 3.11
* Remove pinning of django-treebeard

2.1.0 (2022-03-27)
==================

* Fix add / delete buttons if djangocms-admin-style is not installed


2.0.0 (2020-09-02)
==================

* Added support for Django 3.1
* Dropped support for Python 2.7 and Python 3.4
* Dropped support for Django < 2.2


1.2.0 (2020-01-22)
==================

* Added support for Django 3.0
* Added support for Python 3.8
* Added further tests to raise coverage
* Fixed smaller issues found during testing


1.1.0 (2019-04-16)
==================

* Added support for Django 2.2 and django CMS 3.7
* Removed support for Django 2.0
* Extended test matrix
* Added isort and adapted imports
* Adapted code base to align with other supported addons
* Added translations


1.0.0 (2018-12-13)
==================

* Fixed compatibility with Django 2.x
* Added proper test framework
* Cleaned up file structure


0.4.0 (2018-11-08)
==================

* Added support for Django 1.11, 2.0 and 2.1
* Removed support for Django 1.8, 1.9, 1.10


0.3.0 (2017-07-02)
==================

* Introduced Django 1.10 compatibility
* Fixed a bug (key:value) pairs not saved to database with Django 1.10


0.2.0 (2017-02-28)
==================

* Added Django 1.10 support
* Removed custom lookup options


0.1.2 (2016-11-01)
==================

* Fixed a bug with multiple widgets on the same page


0.1.1 (2016-07-12)
==================

* Fixed styling issues
* Fixed a bug where it wasn't possible to remove freshly created pairs


0.1.0 (2016-06-29)
==================

* Stop forcing Django to use `jsonb` fields on PostgreSQL backends


0.0.6 (2016-06-27)
==================

* Fixed errors when both ``django-jsonfield`` and ``jsonfield``
  are on the python path.


0.0.5 (2016-06-27)
==================

* Fixed ``AttributeError`` when fetching from db.


0.0.4 (2016-06-27)
==================

* Fixed an issue with previous release


0.0.3 (2016-06-26)
==================

* Worked-around Django+Postgress issue
* Fixed appearance of "+" and "x" icons


0.0.2 (2016-06-20)
==================

* Added support to automatically add property/-ies to implementing classes


0.0.1 (2016-06-16)
==================

* Initial release
