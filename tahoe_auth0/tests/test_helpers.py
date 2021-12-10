from unittest.mock import patch

from ddt import data, ddt, unpack
from django.core.exceptions import ImproperlyConfigured
from django.test import TestCase, override_settings

from tahoe_auth0.helpers import (
    auth0_enabled,
    build_auth0_query,
    get_auth0_domain,
    get_client_info,
    is_auth0_enabled,
)


class TestDomain(TestCase):
    @override_settings(TAHOE_AUTH0_CONFIGS={})
    @patch("tahoe_auth0.helpers.configuration_helpers.get_value", return_value=True)
    def test_no_domain(self, mock_get_value):
        with self.assertRaises(ImproperlyConfigured):
            get_auth0_domain()

    @override_settings(TAHOE_AUTH0_CONFIGS={"DOMAIN": "example.auth0.com"})
    @patch("tahoe_auth0.helpers.configuration_helpers.get_value", return_value=True)
    def test_with_domain(self, mock_get_value):
        actual_domain = get_auth0_domain()
        self.assertEqual(actual_domain, "example.auth0.com")


@ddt
class TestClientInfo(TestCase):
    @data(
        {"API_CLIENT_ID": "client-id"},
        {"API_CLIENT_SECRET": "client-secret"},
    )
    def test_missing_info(self, settings):
        message = (
            "Both `API_CLIENT_ID` and `API_CLIENT_SECRET` must be "
            "present in your `TAHOE_AUTH0_CONFIGS`"
        )

        with override_settings(TAHOE_AUTH0_CONFIGS=settings), patch(
            "tahoe_auth0.helpers.configuration_helpers.get_value", return_value=True
        ), self.assertRaisesMessage(ImproperlyConfigured, message):
            get_client_info()

    @override_settings(
        TAHOE_AUTH0_CONFIGS={"API_CLIENT_ID": "cid", "API_CLIENT_SECRET": "secret"}
    )
    @patch("tahoe_auth0.helpers.configuration_helpers.get_value", return_value=True)
    def test_correct_configuration(self, mock_get_value):
        client_id, client_secret = get_client_info()
        self.assertEqual(client_id, "cid")
        self.assertEqual(client_secret, "secret")


class TestBuildAuth0Query(TestCase):
    def test_no_kwargs(self):
        query = build_auth0_query()
        self.assertEqual(query, "")

    def test_empty_kwargs(self):
        query = build_auth0_query(**{})
        self.assertEqual(query, "")

    def test_one_arg(self):
        kwargs = {
            "a": 1,
        }
        query = build_auth0_query(**kwargs)

        # A url-encoded value of a:"1"
        self.assertEqual(query, "a%3A%221%22")

    def test_multiple_args(self):
        kwargs = {
            "a": 1,
            "ab.cd": "some value",
        }
        query = build_auth0_query(**kwargs)

        # A url-encoded value of a:"1"&ab.cd:"some value"
        # Order doesn't matter here.
        self.assertIn(
            query,
            [
                "a%3A%221%22&ab.cd%3A%22some+value%22",
                "ab.cd%3A%22some+value%22&a%3A%221%22",
            ],
        )


@ddt
class TestIsAuth0Enabled(TestCase):
    @unpack
    @data(
        {"configuration_flag": None, "feature_flag": True, "is_enabled": True},
        {"configuration_flag": None, "feature_flag": False, "is_enabled": False},
        {"configuration_flag": True, "feature_flag": True, "is_enabled": True},
        {"configuration_flag": True, "feature_flag": False, "is_enabled": True},
        {"configuration_flag": False, "feature_flag": True, "is_enabled": False},
        {"configuration_flag": False, "feature_flag": False, "is_enabled": False},
    )
    def test_flag_and_configurations_priorities(
        self, configuration_flag, feature_flag, is_enabled
    ):
        """
        A site configuration is of higher order, if nothing is defined in the
        site configurations, we will fallback to settings.FEATURES configuration
        """
        with patch(
            "tahoe_auth0.helpers.configuration_helpers.get_value",
            return_value=configuration_flag,
        ), override_settings(FEATURES={"ENABLE_TAHOE_AUTH0": feature_flag}):
            self.assertEqual(is_enabled, is_auth0_enabled())

    @override_settings(TAHOE_AUTH0_CONFIGS={})
    @patch("tahoe_auth0.helpers.configuration_helpers.get_value", return_value=True)
    def test_flag_enabled_no_settings(self, mock_get_value):
        message = (
            "`TAHOE_AUTH0_CONFIGS` settings must be defined when enabling Tahoe Auth0"
        )
        with self.assertRaisesMessage(ImproperlyConfigured, message):
            is_auth0_enabled()

    @override_settings(TAHOE_AUTH0_CONFIGS=None)
    @patch("tahoe_auth0.helpers.configuration_helpers.get_value", return_value=True)
    def test_flag_enabled_none_settings(self, mock_get_value):
        message = (
            "`TAHOE_AUTH0_CONFIGS` settings must be defined when enabling Tahoe Auth0"
        )
        with self.assertRaisesMessage(ImproperlyConfigured, message):
            is_auth0_enabled()

    @patch("tahoe_auth0.helpers.configuration_helpers.get_value", return_value="True")
    def test_auth0_settings_enabled_not_boolean(self, mock_get_value):
        message = "`ENABLE_TAHOE_AUTH0` must be of boolean type"
        with self.assertRaisesMessage(ImproperlyConfigured, message):
            is_auth0_enabled()

    @override_settings(
        TAHOE_AUTH0_CONFIGS={
            "DOMAIN": "test.com",
            "API_CLIENT_ID": "client-id",
            "API_CLIENT_SECRET": "client-secret",
        },
    )
    @patch("tahoe_auth0.helpers.configuration_helpers.get_value", return_value=True)
    def test_auth0_enabled(self, mock_get_value):
        self.assertEqual(True, is_auth0_enabled())


class TestAuth0EnabledDecorator(TestCase):
    @patch("tahoe_auth0.helpers.is_auth0_enabled", return_value=False)
    def test_not_enabled(self, mock_is_auth0_enabled):
        with self.assertRaises(EnvironmentError):
            auth0_enabled(lambda: 1)()

        mock_is_auth0_enabled.assert_called_once_with()

    @patch("tahoe_auth0.helpers.is_auth0_enabled", return_value=True)
    def test_enabled(self, mock_is_auth0_enabled):
        function_return = auth0_enabled(lambda: 1)()

        mock_is_auth0_enabled.assert_called_once_with()
        self.assertEqual(1, function_return)