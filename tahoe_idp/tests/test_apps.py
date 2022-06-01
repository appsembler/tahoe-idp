"""
Tests TahoeIdpConfig Open edX configuration.
"""

from tahoe_idp.apps import TahoeIdpConfig


def test_app_config():
    assert TahoeIdpConfig.plugin_app == {
        'settings_config': {
            'cms.djangoapp': {
                'common': {
                    'relative_path': 'settings.common'
                },
            },
            'lms.djangoapp': {
                'common': {
                    'relative_path': 'settings.common'
                },
            }
        },
        'url_config': {
            'cms.djangoapp': {
                'namespace': 'tahoe_idp',
                'app_name': 'tahoe_idp'
            },
            'lms.djangoapp': {
                'namespace': 'tahoe_idp',
                'app_name': 'tahoe_idp'
            }
        }
    }, 'Should initiate the app as an Open edX plugin.'
