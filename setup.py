#!/usr/bin/env python
# -*- coding: utf-8 -*-
from setuptools import setup
from djangocms_attributes_field import __version__


# https://pypi.python.org/pypi?%3Aaction=list_classifiers
CLASSIFIERS = [
    'Development Status :: 5 - Production/Stable',
    'Environment :: Web Environment',
    'Framework :: Django',
    'Framework :: Django :: 1.8',
    'Framework :: Django :: 1.9',
    'Intended Audience :: Developers',
    'License :: OSI Approved :: BSD License',
    'Operating System :: OS Independent',
    'Programming Language :: Python',
    'Topic :: Communications',
    'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
    'Topic :: Internet :: WWW/HTTP :: Dynamic Content :: Message Boards',
    'Programming Language :: Python :: 2.7',
    'Programming Language :: Python :: 3.3',
    'Programming Language :: Python :: 3.4',
    'Programming Language :: Python :: 3.5',
]

REQUIREMENTS = [
    'django>=1.8,<1.10',
]

setup(
    name='djangocms-attributes-field',
    version=__version__,
    description='',
    author='Divio AG',
    author_email='info@divio.ch',
    url='https://github.com/divio/djangocms-attributes-field/',
    packages=['djangocms_attributes_field', ],
    install_requires=REQUIREMENTS,
    license='LICENSE.txt',
    platforms=['OS Independent'],
    classifiers=CLASSIFIERS,
    long_description=open('README.rst').read(),
    include_package_data=True,
    zip_safe=False,
)
