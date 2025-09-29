# AAP 2.5 ONLY - DO NOT FORWARD PORT: Single-assertion Platform Auditor property tests
# AIA: Primarily AI, New content, Human-initiated, Reviewed, Claude (Anthropic AI) via Claude Code
# AIA PAI Nc Hin R Claude Code - https://aiattribution.github.io/interpret-attribution
import pytest
from unittest.mock import patch, MagicMock
from ansible_base.rbac.models import RoleUserAssignment
from awx.main.models import get_platform_auditor_role


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
def test_user_is_platform_auditor(alice, setup_managed_roles):
    """Test that is_platform_auditor property works correctly."""
    # Assign Platform Auditor role
    platform_role = get_platform_auditor_role()
    RoleUserAssignment.objects.create(user=alice, role_definition=platform_role)

    # Clear cache and test property
    if hasattr(alice, '_is_platform_auditor'):
        delattr(alice, '_is_platform_auditor')

    assert alice.is_platform_auditor is True


@pytest.mark.django_db
def test_user_is_auditor_with_system_auditor(alice, setup_managed_roles):
    """Test that is_auditor property works with system auditor."""
    alice.is_system_auditor = True
    alice.save()

    assert alice.is_auditor is True


@pytest.mark.django_db
def test_user_is_auditor_with_platform_auditor(alice, setup_managed_roles):
    """Test that is_auditor property works with platform auditor."""
    # Assign Platform Auditor role
    platform_role = get_platform_auditor_role()
    RoleUserAssignment.objects.create(user=alice, role_definition=platform_role)

    # Clear cache and test property
    if hasattr(alice, '_is_platform_auditor'):
        delattr(alice, '_is_platform_auditor')

    assert alice.is_auditor is True


# END AI Contribution
