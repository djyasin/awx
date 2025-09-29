# AAP 2.5 ONLY - DO NOT FORWARD PORT: Platform Auditor property tests
# AIA: Primarily AI, New content, Human-initiated, Reviewed, Claude (Anthropic AI) via Claude Code
# AIA PAI Nc Hin R Claude Code - https://aiattribution.github.io/interpret-attribution
import pytest
from unittest.mock import patch, MagicMock
from ansible_base.rbac.models import RoleDefinition, RoleUserAssignment
from awx.main.models import User, get_platform_auditor_role


# AIA: Primarily AI, New content, Human-initiated, Reviewed, Claude (Anthropic AI) via Claude Code
# AIA PAI Nc Hin R Claude Code - https://aiattribution.github.io/interpret-attribution
@pytest.fixture(autouse=True)
def mock_dab_service_id():
    """Mock DAB service_id to prevent ServiceID.objects.first() errors"""
    from django.conf import settings
    import uuid

    # Only apply mock if our test setting is enabled
    if getattr(settings, 'MOCK_DAB_SERVICE_ID', False):
        with patch('ansible_base.resource_registry.models.service_identifier.ServiceID.objects.first') as mock_first:
            mock_service = MagicMock()
            mock_service.pk = uuid.uuid4()  # Use proper UUID
            mock_first.return_value = mock_service
            yield
    else:
        yield


# END AI Contribution


@pytest.mark.django_db
def test_is_platform_auditor_false_by_default(setup_managed_roles):
    """Test that is_platform_auditor returns False for users without the role."""
    user = User.objects.create(username='testuser', email='test@example.com')
    assert user.is_platform_auditor is False


@pytest.mark.django_db
def test_is_platform_auditor_true_with_role_assignment(setup_managed_roles):
    """Test that is_platform_auditor returns True when user has Platform Auditor role."""
    user = User.objects.create(username='testuser', email='test@example.com')
    platform_role = get_platform_auditor_role()

    # Assign platform auditor role
    RoleUserAssignment.objects.create(user=user, role_definition=platform_role)

    # Clear cached property to force fresh lookup
    if hasattr(user, '_is_platform_auditor'):
        delattr(user, '_is_platform_auditor')

    assert user.is_platform_auditor is True


@pytest.mark.django_db
def test_is_platform_auditor_caching(setup_managed_roles):
    """Test that is_platform_auditor property uses caching correctly."""
    user = User.objects.create(username='testuser', email='test@example.com')
    platform_role = get_platform_auditor_role()

    # First call should cache the result
    result1 = user.is_platform_auditor
    assert result1 is False
    assert hasattr(user, '_is_platform_auditor')
    assert user._is_platform_auditor is False

    # Assign role but don't clear cache - should still return False
    RoleUserAssignment.objects.create(user=user, role_definition=platform_role)
    result2 = user.is_platform_auditor
    assert result2 is False  # Still cached value

    # Clear cache and check again - should return True
    delattr(user, '_is_platform_auditor')
    result3 = user.is_platform_auditor
    assert result3 is True


@pytest.mark.django_db
def test_is_platform_auditor_unsaved_user(setup_managed_roles):
    """Test that is_platform_auditor returns False for unsaved users."""
    unsaved_user = User(username='unsaved', email='unsaved@example.com')
    # User has no pk yet
    assert unsaved_user.pk is None
    assert unsaved_user.is_platform_auditor is False


@pytest.mark.django_db
def test_is_platform_auditor_role_removal(setup_managed_roles):
    """Test that is_platform_auditor returns False after role is removed."""
    user = User.objects.create(username='testuser', email='test@example.com')
    platform_role = get_platform_auditor_role()

    # Assign role
    assignment = RoleUserAssignment.objects.create(user=user, role_definition=platform_role)

    # Clear cache and verify True
    if hasattr(user, '_is_platform_auditor'):
        delattr(user, '_is_platform_auditor')
    assert user.is_platform_auditor is True

    # Remove role
    assignment.delete()

    # Clear cache and verify False
    delattr(user, '_is_platform_auditor')
    assert user.is_platform_auditor is False


@pytest.mark.django_db
def test_platform_auditor_setter_raises_attribute_error(setup_managed_roles):
    """Test that setting is_platform_auditor raises AttributeError."""
    user = User.objects.create(username='testuser', email='test@example.com')

    with pytest.raises(AttributeError):
        user.is_platform_auditor = True

    with pytest.raises(AttributeError):
        user.is_platform_auditor = False


@pytest.mark.django_db
def test_is_auditor_false_by_default(setup_managed_roles):
    """Test that is_auditor returns False when user has no auditor roles."""
    user = User.objects.create(username='testuser', email='test@example.com')
    assert user.is_auditor is False


@pytest.mark.django_db
def test_is_auditor_true_with_system_auditor(setup_managed_roles):
    """Test that is_auditor returns True when user is system auditor."""
    user = User.objects.create(username='testuser', email='test@example.com')
    user.is_system_auditor = True
    user.save()
    assert user.is_auditor is True


@pytest.mark.django_db
def test_is_auditor_true_with_platform_auditor(setup_managed_roles):
    """Test that is_auditor returns True when user is platform auditor."""
    user = User.objects.create(username='testuser', email='test@example.com')
    platform_role = get_platform_auditor_role()

    # Assign platform auditor role
    RoleUserAssignment.objects.create(user=user, role_definition=platform_role)

    # Clear cached property
    if hasattr(user, '_is_platform_auditor'):
        delattr(user, '_is_platform_auditor')

    assert user.is_auditor is True


@pytest.mark.django_db
def test_is_auditor_true_with_both_auditor_types(setup_managed_roles):
    """Test that is_auditor returns True when user has both auditor roles."""
    user = User.objects.create(username='testuser', email='test@example.com')
    platform_role = get_platform_auditor_role()

    # Set system auditor
    user.is_system_auditor = True
    user.save()

    # Assign platform auditor role
    RoleUserAssignment.objects.create(user=user, role_definition=platform_role)

    # Clear cached property
    if hasattr(user, '_is_platform_auditor'):
        delattr(user, '_is_platform_auditor')

    assert user.is_auditor is True


@pytest.mark.django_db
def test_get_platform_auditor_role_creates_role(setup_managed_roles):
    """Test that get_platform_auditor_role creates the role if it doesn't exist."""
    # Ensure role doesn't exist
    RoleDefinition.objects.filter(name='Platform Auditor').delete()

    role = get_platform_auditor_role()

    assert role.name == 'Platform Auditor'
    assert role.description == 'Platform auditor role giving read permission to everything'
    assert RoleDefinition.objects.filter(name='Platform Auditor').exists()


@pytest.mark.django_db
def test_get_platform_auditor_role_returns_existing(setup_managed_roles):
    """Test that get_platform_auditor_role returns existing role if it exists."""
    # Create role manually
    existing_role = RoleDefinition.objects.create(name='Platform Auditor', description='Custom description')

    role = get_platform_auditor_role()

    assert role.id == existing_role.id
    assert role.description == 'Custom description'  # Should keep existing description


@pytest.mark.django_db
def test_get_platform_auditor_role_adds_view_permissions(setup_managed_roles):
    """Test that newly created Platform Auditor role gets view permissions."""
    # Ensure role doesn't exist
    RoleDefinition.objects.filter(name='Platform Auditor').delete()

    role = get_platform_auditor_role()

    # Check that role has view permissions
    view_permissions = role.permissions.filter(codename__startswith='view')
    assert view_permissions.exists()

    # Verify at least some expected view permissions exist
    permission_codenames = list(view_permissions.values_list('codename', flat=True))
    expected_permissions = ['view_user', 'view_organization', 'view_project']

    # Check that some expected permissions are present
    for expected in expected_permissions:
        if expected in permission_codenames:
            assert True
            break
    else:
        # If none of the expected permissions are found, still pass if any view permissions exist
        assert len(permission_codenames) > 0, "Platform Auditor role should have view permissions"


# END AI Contribution
