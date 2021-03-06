"""
Tests for the permission module.
"""

from tahoe_idp.permissions import (
    get_role_with_default,
    is_organization_admin,
    is_organization_staff,
)


def test_organization_admin():
    """
    Tests for the is_organization_admin helper.
    """
    assert is_organization_admin('Administrator'), 'Administrator, is admin!'
    assert not is_organization_admin('Staff'), 'Staff is not an admin'
    assert not is_organization_admin('Learner'), 'Learner is not an admin'
    assert not is_organization_admin('SomethingElse'), 'Helper should be safe to use for new roles'


def test_organization_staff():
    """
    Tests for the is_organization_staff helper.
    """
    assert is_organization_staff('Administrator'), 'Administrator, is also Staff'
    assert is_organization_staff('Staff'), 'Staff, is Staff'
    assert not is_organization_staff('Learner'), 'Learner is not an staff'
    assert not is_organization_staff('SomethingElse'), 'Helper should be safe to use for new roles'


def test_get_role_with_default():
    """
    Tests for the `get_role_with_default` helper.
    """
    assert get_role_with_default(user_data={}) == 'learner', 'Default to learner'

    assert get_role_with_default(user_data={
        'platform_role': 'Administrator',
    }) == 'Administrator', 'Should read the provided `Administrator` role correctly'

    assert get_role_with_default(user_data={
        'platform_role': 'Learner',
    }) == 'Learner', 'Should read the provided `Learner` role correctly'
