import pytest
from unittest.mock import patch, MagicMock

from prometheus_client.parser import text_string_to_metric_families
from awx.main import models
from awx.main.analytics.metrics import metrics
from awx.api.versioning import reverse


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

EXPECTED_VALUES = {
    'awx_system_info': 1.0,
    'awx_organizations_total': 1.0,
    'awx_users_total': 1.0,
    'awx_teams_total': 1.0,
    'awx_inventories_total': 1.0,
    'awx_projects_total': 1.0,
    'awx_job_templates_total': 1.0,
    'awx_workflow_job_templates_total': 1.0,
    'awx_hosts_total': 1.0,
    'awx_hosts_total': 1.0,
    'awx_schedules_total': 1.0,
    'awx_sessions_total': 0.0,
    'awx_status_total': 0.0,
    'awx_running_jobs_total': 0.0,
    'awx_instance_capacity': 100.0,
    'awx_instance_consumed_capacity': 0.0,
    'awx_instance_remaining_capacity': 100.0,
    'awx_instance_cpu': 0.0,
    'awx_instance_memory': 0.0,
    'awx_instance_info': 1.0,
    'awx_license_instance_total': 0,
    'awx_license_instance_free': 0,
    'awx_pending_jobs_total': 0,
    'awx_database_connections_total': 1,
}


@pytest.mark.django_db
def test_metrics_counts(organization_factory, job_template_factory, workflow_job_template_factory):
    objs = organization_factory('org', superusers=['admin'])
    jt = job_template_factory('test', organization=objs.organization, inventory='test_inv', project='test_project', credential='test_cred')
    workflow_job_template_factory('test')
    models.Team(organization=objs.organization).save()
    models.Host(inventory=jt.inventory).save()
    models.Schedule(rrule='DTSTART;TZID=America/New_York:20300504T150000', unified_job_template=jt.job_template).save()

    output = metrics()
    gauges = text_string_to_metric_families(output.decode('UTF-8'))

    for gauge in gauges:
        for sample in gauge.samples:
            # name, label, value, timestamp, exemplar
            name, _, value, _, _ = sample
            assert EXPECTED_VALUES[name] == value


def get_metrics_view_db_only():
    return reverse('api:metrics_view') + '?dbonly=1'


@pytest.mark.django_db
def test_metrics_permissions(get, admin, org_admin, alice, bob, organization):
    assert get(get_metrics_view_db_only(), user=admin).status_code == 200
    assert get(get_metrics_view_db_only(), user=org_admin).status_code == 403
    assert get(get_metrics_view_db_only(), user=alice).status_code == 403
    assert get(get_metrics_view_db_only(), user=bob).status_code == 403
    organization.auditor_role.members.add(bob)
    assert get(get_metrics_view_db_only(), user=bob).status_code == 403

    bob.is_system_auditor = True
    assert get(get_metrics_view_db_only(), user=bob).status_code == 200


# AAP 2.5 ONLY - DO NOT FORWARD PORT: Platform Auditor metrics access tests
# AIA: Primarily AI, New content, Human-initiated, Reviewed, Claude (Anthropic AI) via Claude Code
# AIA PAI Nc Hin R Claude Code - https://aiattribution.github.io/interpret-attribution
@pytest.mark.django_db
def test_metrics_platform_auditor_permissions(get, alice, setup_managed_roles):
    """Test that Platform Auditor users can access metrics endpoint."""
    from ansible_base.rbac.models import RoleUserAssignment
    from awx.main.models import get_platform_auditor_role

    # Initially should be denied access
    assert get(get_metrics_view_db_only(), user=alice).status_code == 403

    # Assign Platform Auditor role
    platform_role = get_platform_auditor_role()
    assignment = RoleUserAssignment.objects.create(user=alice, role_definition=platform_role)

    # Clear cached property to ensure fresh lookup
    if hasattr(alice, '_is_platform_auditor'):
        delattr(alice, '_is_platform_auditor')

    # Should now have access
    assert get(get_metrics_view_db_only(), user=alice).status_code == 200

    # Verify user properties are working correctly
    assert alice.is_platform_auditor is True
    assert alice.is_auditor is True
    assert alice.is_system_auditor is False

    # Remove role and verify access is revoked
    assignment.delete()
    delattr(alice, '_is_platform_auditor')
    assert get(get_metrics_view_db_only(), user=alice).status_code == 403


@pytest.mark.django_db
def test_metrics_combined_auditor_permissions(get, bob, setup_managed_roles):
    """Test that users with both system and platform auditor roles work correctly."""
    from ansible_base.rbac.models import RoleUserAssignment
    from awx.main.models import get_platform_auditor_role

    # Set as system auditor
    bob.is_system_auditor = True
    bob.save()

    # Should have access via system auditor
    assert get(get_metrics_view_db_only(), user=bob).status_code == 200

    # Also assign Platform Auditor role
    platform_role = get_platform_auditor_role()
    RoleUserAssignment.objects.create(user=bob, role_definition=platform_role)

    # Clear cached property
    if hasattr(bob, '_is_platform_auditor'):
        delattr(bob, '_is_platform_auditor')

    # Should still have access and both properties should be True
    assert get(get_metrics_view_db_only(), user=bob).status_code == 200
    assert bob.is_system_auditor is True
    assert bob.is_platform_auditor is True
    assert bob.is_auditor is True


@pytest.mark.django_db
def test_metrics_auditor_property_usage(get, alice, bob, setup_managed_roles):
    """Test that metrics endpoint correctly uses the is_auditor convenience property."""
    from ansible_base.rbac.models import RoleUserAssignment
    from awx.main.models import get_platform_auditor_role

    # Test platform auditor access via is_auditor property
    platform_role = get_platform_auditor_role()
    RoleUserAssignment.objects.create(user=alice, role_definition=platform_role)
    if hasattr(alice, '_is_platform_auditor'):
        delattr(alice, '_is_platform_auditor')

    # Test system auditor access via is_auditor property
    bob.is_system_auditor = True
    bob.save()

    # Both should have access through the is_auditor property
    assert get(get_metrics_view_db_only(), user=alice).status_code == 200
    assert get(get_metrics_view_db_only(), user=bob).status_code == 200

    # Verify the is_auditor property works correctly for both
    assert alice.is_auditor is True
    assert bob.is_auditor is True


# END AI Contribution


@pytest.mark.django_db
def test_metrics_http_methods(get, post, patch, put, options, admin):
    assert get(get_metrics_view_db_only(), user=admin).status_code == 200
    assert put(get_metrics_view_db_only(), user=admin).status_code == 405
    assert patch(get_metrics_view_db_only(), user=admin).status_code == 405
    assert post(get_metrics_view_db_only(), user=admin).status_code == 405
    assert options(get_metrics_view_db_only(), user=admin).status_code == 200
