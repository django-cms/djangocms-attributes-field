#!/usr/bin/env python
HELPER_SETTINGS = {
    'SECRET_KEY': 'HAPPY_NOW?',
    'INSTALLED_APPS': [
        'djangocms_attributes_field',
        'tests.test_app',
    ],
    'CMS_LANGUAGES': {
        1: [{
            'code': 'en',
            'name': 'English',
        }]
    },
    'LANGUAGE_CODE': 'en',
    'ALLOWED_HOSTS': ['localhost'],
}


def run():
    from app_helper import runner
    runner.cms('djangocms_attributes_field')


if __name__ == '__main__':
    run()
