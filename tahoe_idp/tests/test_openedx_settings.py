"""
Tests for the openedx production.py settings.
"""
import pytest
from django.core.exceptions import ImproperlyConfigured

from tahoe_idp.settings import (
    cms_production,
    common_production,
    lms_production,
)


def test_lms_tpa_backend_settings(settings):
    """
    Test settings third party auth backends.
    """
    settings.AUTHENTICATION_BACKENDS = ['dummy_backend']
    lms_production.plugin_settings(settings)

    backend_path = 'tahoe_idp.backend.TahoeIdpOAuth2'
    assert backend_path == settings.AUTHENTICATION_BACKENDS[0], 'TahoeIdpOAuth2 goes first'

    lms_production.plugin_settings(settings)
    assert settings.AUTHENTICATION_BACKENDS.count(backend_path) == 1, 'adds only one instance'


def test_cms_authentication_backend_settings(settings):
    """
    Test settings third party auth backends.
    """
    settings.AUTHENTICATION_BACKENDS = ['some_other_backend']
    backend_path = 'tahoe_idp.magiclink_backends.MagicLinkBackend'

    cms_production.plugin_settings(settings)
    assert backend_path == settings.AUTHENTICATION_BACKENDS[0], 'MagicLinkBackend goes first'

    cms_production.plugin_settings(settings)
    assert settings.AUTHENTICATION_BACKENDS.count(backend_path) == 1, 'add only one instance'


@pytest.mark.parametrize('invalid_test_case', [
    {
        'name': 'MAGICLINK_TOKEN_LENGTH',
        'value': 'not integer',
        'message': '"MAGICLINK_TOKEN_LENGTH" must be an integer',
    },
    {
        'name': 'MAGICLINK_AUTH_TIMEOUT',
        'value': 'some weird value',
        'message': '"MAGICLINK_AUTH_TIMEOUT" must be an integer',
    },
    {
        'name': 'MAGICLINK_LOGIN_REQUEST_TIME_LIMIT',
        'value': 'not integer',
        'message': '"MAGICLINK_LOGIN_REQUEST_TIME_LIMIT" must be an integer',
    },
])
def test_wrong_magiclink_settings(settings, invalid_test_case):
    """
    Tests a couple of bad configuration to ensure proper error messages are raised.
    """
    setattr(settings, invalid_test_case['name'], invalid_test_case['value'])

    with pytest.raises(ImproperlyConfigured, match=invalid_test_case['message']):
        common_production.magiclink_settings(settings)


def test_token_length_configs(settings):
    """
    Ensure MAGICLINK_TOKEN_LENGTH is validated for security.
    """
    common_production.magiclink_settings(settings)
    assert settings.MAGICLINK_TOKEN_LENGTH == 50, 'default to 50'

    settings.MAGICLINK_TOKEN_LENGTH = 19
    common_production.magiclink_settings(settings)
    assert settings.MAGICLINK_TOKEN_LENGTH == 20, 'do not allow less than 20'

    settings.MAGICLINK_TOKEN_LENGTH = 60
    common_production.magiclink_settings(settings)
    assert settings.MAGICLINK_TOKEN_LENGTH == 60, 'allow setting any large value'
