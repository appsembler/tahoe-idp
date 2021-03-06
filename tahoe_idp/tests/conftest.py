"""
Pytest helpers.
"""

import pytest

from site_config_client.openedx.test_helpers import override_site_config

import tahoe_idp.helpers

MOCK_TENANT_ID = '479d8c4e-d441-11ec-8ebb-6f8318ddff9a'
MOCK_CLIENT_ID = 'a-key'
MOCK_CLIENT_SECRET = 'a-secret-key'


@pytest.fixture(scope='function')
def mock_tahoe_idp_settings(monkeypatch, settings):
    """
    Mock configs to enable Tahoe IdP and set TAHOE_IDP_CONFIGS.
    """
    def mock_is_tahoe_idp_enabled():
        """Mock for `is_tahoe_idp_enabled` to return always True."""
        return True

    settings.TAHOE_IDP_CONFIGS = {
        'BASE_URL': 'https://domain',
        'API_KEY': 'dummy-client-secret',
    }

    monkeypatch.setattr(tahoe_idp.helpers, 'is_tahoe_idp_enabled', mock_is_tahoe_idp_enabled)


def mock_tahoe_idp_api_settings(test_func):
    """
    Mock API related configuration and settings to make API calls easier in tests.
    """
    admin_patch = override_site_config(
        config_type='admin',
        TAHOE_IDP_TENANT_ID=MOCK_TENANT_ID,
        TAHOE_IDP_CLIENT_ID=MOCK_CLIENT_ID,
    )
    secret_patch = override_site_config(
        config_type='secret',
        TAHOE_IDP_CLIENT_SECRET=MOCK_CLIENT_SECRET,
    )
    return secret_patch(admin_patch(test_func))
