"""
AWX Settings for Isolated Testing

This settings module provides a fully isolated testing environment that:
- Uses SQLite instead of PostgreSQL for faster, isolated test runs
- Disables DAB (django-ansible-base) resource sync to prevent 401 errors
- Mocks DAB ServiceID dependencies to avoid database table requirements
- Provides in-memory caching for test isolation

Usage:
    pytest --ds=awx.main.tests.settings_for_isolated_testing [test_file]

Key Features:
- SQLite Database: Eliminates PostgreSQL dependency and permission issues
- DAB Resource Sync Disabled: Prevents 401 errors when creating RoleUserAssignment objects
- ServiceID Mocking: Test fixtures can mock DAB ServiceID.objects.first() calls
- Task Mocking: DISPATCHER_MOCK_PUBLISH=True disables actual task submission
- Memory Caching: Each test run gets isolated cache instance

This is ideal for Platform Auditor testing and other RBAC-related tests that
interact with django-ansible-base components.

FORWARD PORT NOTES FOR 2.6+:
The testing infrastructure in this file should be forward ported as it provides
valuable DAB testing capabilities. Key components to preserve:

1. ServiceID Mocking Pattern:
   Sample fixture code pattern to add to test files to prevent: "AttributeError: 'NoneType' object has no attribute 'pk'"

   # Mock the service_id field default for testing when DAB resource registry tries to access ServiceID.objects.first().pk
   @pytest.fixture(autouse=True)
   def mock_dab_service_id():
       from django.conf import settings
       import uuid

       if getattr(settings, 'MOCK_DAB_SERVICE_ID', False):
           with patch('ansible_base.resource_registry.models.service_identifier.ServiceID.objects.first') as mock_first:
               mock_service = MagicMock()
               mock_service.pk = uuid.uuid4()
               mock_first.return_value = mock_service
               yield
       else:
           yield

   - MOCK_DAB_SERVICE_ID setting to enable/disable mocking
   - Added to test files in 2.5 only: test_metrics.py, test_settings.py, test_platform_auditor.py, test_user_auditor_properties.py

2. DAB Resource Server Isolation:
   - RESOURCE_SERVER = {} setting disables DAB sync during testing
   - Prevents 401 authentication errors in test environments

3. SQLite Testing Configuration:
   - Fast, isolated test database setup
   - No PostgreSQL permissions or setup required

While Platform Auditor-specific tests are AAP 2.5 only and should NOT be forward ported,
the underlying test infrastructure pattern is valuable for any future DAB-related testing.

AIA: Primarily AI, New content, Human-initiated, Reviewed, Claude (Anthropic AI) via Claude Code
AIA PAI Nc Hin R Claude Code - https://aiattribution.github.io/interpret-attribution
"""

# Python
import uuid

# Load development settings for base variables.
from awx.settings.development import *  # NOQA

# Some things make decisions based on settings.SETTINGS_MODULE, so this is done for that
SETTINGS_MODULE = 'awx.settings.development'

# Turn off task submission, because sqlite3 does not have pg_notify
DISPATCHER_MOCK_PUBLISH = True

# Use SQLite for unit tests instead of PostgreSQL.  If the lines below are
# commented out, Django will create the test_awx-dev database in PostgreSQL to
# run unit tests.
CACHES = {'default': {'BACKEND': 'django.core.cache.backends.locmem.LocMemCache', 'LOCATION': 'unique-{}'.format(str(uuid.uuid4()))}}
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'awx.sqlite3'),  # noqa
        'TEST': {
            # Test database cannot be :memory: for inventory tests.
            'NAME': os.path.join(BASE_DIR, 'awx_test.sqlite3')  # noqa
        },
    }
}

# Disable DAB resource sync to Gateway/Resource Server for testing
# This prevents 401 errors when creating RoleUserAssignment objects in tests
# since test users don't exist in the Gateway system
# Set empty dict to disable sync (code checks for URL key)
RESOURCE_SERVER = {}

# This flag enables DAB ServiceID mocking in test files via autouse fixtures (see block comment above)
MOCK_DAB_SERVICE_ID = True
