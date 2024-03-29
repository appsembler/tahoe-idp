"""
Tests TahoeIdpConfig Open edX configuration.
"""

from tahoe_idp.apps import TahoeIdpConfig


def test_app_config():
    assert TahoeIdpConfig.plugin_app == {
        'settings_config': {
            'cms.djangoapp': {
                'production': {  # Needs to be production settings, otherwise devstack will override it
                    'relative_path': 'settings.cms_production',  # Use cms-settings
                },
            },
            'lms.djangoapp': {
                'production': {  # Needs to be production settings, otherwise devstack will override it
                    'relative_path': 'settings.lms_production',  # Use lms-settings
                },
            },
        },
        'url_config': {
            'cms.djangoapp': {
                'namespace': 'tahoe_idp',
                'app_name': 'tahoe_idp',
            },
            'lms.djangoapp': {
                'namespace': 'tahoe_idp',
                'app_name': 'tahoe_idp',
            },
        },
        'signals_config': {
            'lms.djangoapp': {
                'relative_path': 'receivers',
                'receivers': [
                    {
                        'receiver_func_name': 'user_sync_to_idp',
                        'signal_path': 'django.db.models.signals.post_save',
                        'sender_path': 'django.contrib.auth.models.User',
                    },
                    {
                        'receiver_func_name': 'user_sync_to_idp',
                        'signal_path': 'django.db.models.signals.post_save',
                        'sender_path': 'student.models.UserProfile',
                    },
                ],
            },
            'cms.djangoapp': {
                'relative_path': 'receivers',
                'receivers': [
                    {
                        'receiver_func_name': 'user_sync_to_idp',
                        'signal_path': 'django.db.models.signals.post_save',
                        'sender_path': 'django.contrib.auth.models.User',
                    },
                    {
                        'receiver_func_name': 'user_sync_to_idp',
                        'signal_path': 'django.db.models.signals.post_save',
                        'sender_path': 'student.models.UserProfile',
                    },
                ],
            },
        }
    }, 'Should initiate the app as an Open edX plugin.'
