# Copyright (c) 2018 Red Hat, Inc.
# All Rights Reserved.

# Python
import logging

# Django
from django.db.models import Count, OuterRef, Subquery, TextField
from django.db.models.functions import Cast, Coalesce
from django.contrib.contenttypes.models import ContentType
from django.utils.translation import gettext_lazy as _

# AWX
from ansible_base.rbac.models import RoleDefinition, RoleUserAssignment
from awx.main.models import (
    ActivityStream,
    Inventory,
    Host,
    Project,
    ExecutionEnvironment,
    JobTemplate,
    WorkflowJobTemplate,
    Organization,
    NotificationTemplate,
    Role,
    User,
    Team,
    InstanceGroup,
    Credential,
)
from awx.api.generics import (
    ListCreateAPIView,
    RetrieveUpdateDestroyAPIView,
    SubListAPIView,
    SubListCreateAttachDetachAPIView,
    SubListAttachDetachAPIView,
    SubListCreateAPIView,
    ResourceAccessList,
    BaseUsersList,
)

from awx.api.serializers import (
    OrganizationSerializer,
    InventorySerializer,
    UserSerializer,
    TeamSerializer,
    ActivityStreamSerializer,
    RoleSerializer,
    NotificationTemplateSerializer,
    InstanceGroupSerializer,
    ExecutionEnvironmentSerializer,
    ProjectSerializer,
    JobTemplateSerializer,
    WorkflowJobTemplateSerializer,
    CredentialSerializer,
)
from awx.api.views.mixin import RelatedJobsPreventDeleteMixin, OrganizationCountsMixin, OrganizationInstanceGroupMembershipMixin
from awx.api.views import immutablesharedfields

logger = logging.getLogger('awx.api.views.organization')


@immutablesharedfields
class OrganizationList(OrganizationCountsMixin, ListCreateAPIView):
    model = Organization
    serializer_class = OrganizationSerializer


@immutablesharedfields
class OrganizationDetail(RelatedJobsPreventDeleteMixin, RetrieveUpdateDestroyAPIView):
    model = Organization
    serializer_class = OrganizationSerializer

    def get_serializer_context(self, *args, **kwargs):
        full_context = super(OrganizationDetail, self).get_serializer_context(*args, **kwargs)

        if not hasattr(self, 'kwargs') or 'pk' not in self.kwargs:
            return full_context
        org_id = int(self.kwargs['pk'])

        org_counts = {}
        access_kwargs = {'accessor': self.request.user, 'role_field': 'read_role'}
        member_rd_names = ['Organization Member', 'Controller Organization Member']
        admin_rd_names = ['Organization Admin', 'Controller Organization Admin']

        if RoleDefinition.objects.filter(name__in=member_rd_names).exists():

            def assignment_count(rd_names):
                return Coalesce(
                    Subquery(
                        RoleUserAssignment.objects.filter(
                            object_id=Cast(OuterRef('pk'), output_field=TextField()),
                            role_definition__name__in=rd_names,
                        )
                        .values('object_id')
                        .annotate(c=Count('pk'))
                        .values('c')
                    ),
                    0,
                )

            direct_counts = (
                Organization.objects.filter(id=org_id)
                .annotate(
                    users=assignment_count(member_rd_names),
                    admins=assignment_count(admin_rd_names),
                )
                .values('users', 'admins')
            )

            if direct_counts:
                org_counts = direct_counts[0]
        else:
            org_counts = {'users': 0, 'admins': 0}

        if not org_counts:
            return full_context
        org_counts['inventories'] = Inventory.accessible_objects(**access_kwargs).filter(organization__id=org_id).count()
        org_counts['teams'] = Team.accessible_objects(**access_kwargs).filter(organization__id=org_id).count()
        org_counts['projects'] = Project.accessible_objects(**access_kwargs).filter(organization__id=org_id).count()
        org_counts['job_templates'] = JobTemplate.accessible_objects(**access_kwargs).filter(organization__id=org_id).count()
        org_counts['hosts'] = Host.objects.org_active_count(org_id)

        full_context['related_field_counts'] = {}
        full_context['related_field_counts'][org_id] = org_counts

        return full_context


class OrganizationInventoriesList(SubListAPIView):
    model = Inventory
    serializer_class = InventorySerializer
    parent_model = Organization
    relationship = 'inventories'


@immutablesharedfields
class OrganizationUsersList(BaseUsersList):
    model = User
    serializer_class = UserSerializer
    parent_model = Organization
    relationship = 'member_role.members'
    ordering = ('username',)


@immutablesharedfields
class OrganizationAdminsList(BaseUsersList):
    model = User
    serializer_class = UserSerializer
    parent_model = Organization
    relationship = 'admin_role.members'
    ordering = ('username',)


class OrganizationProjectsList(SubListCreateAPIView):
    model = Project
    serializer_class = ProjectSerializer
    parent_model = Organization
    parent_key = 'organization'


class OrganizationExecutionEnvironmentsList(SubListCreateAttachDetachAPIView):
    model = ExecutionEnvironment
    serializer_class = ExecutionEnvironmentSerializer
    parent_model = Organization
    relationship = 'executionenvironments'
    parent_key = 'organization'
    swagger_topic = "Execution Environments"


class OrganizationJobTemplatesList(SubListCreateAPIView):
    model = JobTemplate
    serializer_class = JobTemplateSerializer
    parent_model = Organization
    parent_key = 'organization'


class OrganizationWorkflowJobTemplatesList(SubListCreateAPIView):
    model = WorkflowJobTemplate
    serializer_class = WorkflowJobTemplateSerializer
    parent_model = Organization
    parent_key = 'organization'


@immutablesharedfields
class OrganizationTeamsList(SubListCreateAttachDetachAPIView):
    model = Team
    serializer_class = TeamSerializer
    parent_model = Organization
    relationship = 'teams'
    parent_key = 'organization'


class OrganizationActivityStreamList(SubListAPIView):
    model = ActivityStream
    serializer_class = ActivityStreamSerializer
    parent_model = Organization
    relationship = 'activitystream_set'
    search_fields = ('changes',)


class OrganizationNotificationTemplatesList(SubListCreateAttachDetachAPIView):
    model = NotificationTemplate
    serializer_class = NotificationTemplateSerializer
    parent_model = Organization
    relationship = 'notification_templates'
    parent_key = 'organization'


class OrganizationNotificationTemplatesAnyList(SubListCreateAttachDetachAPIView):
    model = NotificationTemplate
    serializer_class = NotificationTemplateSerializer
    parent_model = Organization


class OrganizationNotificationTemplatesStartedList(OrganizationNotificationTemplatesAnyList):
    relationship = 'notification_templates_started'


class OrganizationNotificationTemplatesErrorList(OrganizationNotificationTemplatesAnyList):
    relationship = 'notification_templates_error'


class OrganizationNotificationTemplatesSuccessList(OrganizationNotificationTemplatesAnyList):
    relationship = 'notification_templates_success'


class OrganizationNotificationTemplatesApprovalList(OrganizationNotificationTemplatesAnyList):
    relationship = 'notification_templates_approvals'


class OrganizationInstanceGroupsList(OrganizationInstanceGroupMembershipMixin, SubListAttachDetachAPIView):
    model = InstanceGroup
    serializer_class = InstanceGroupSerializer
    parent_model = Organization
    relationship = 'instance_groups'
    filter_read_permission = False


class OrganizationGalaxyCredentialsList(SubListAttachDetachAPIView):
    model = Credential
    serializer_class = CredentialSerializer
    parent_model = Organization
    relationship = 'galaxy_credentials'
    filter_read_permission = False

    def is_valid_relation(self, parent, sub, created=False):
        if sub.kind != 'galaxy_api_token':
            return {'msg': _(f"Credential must be a Galaxy credential, not {sub.credential_type.name}.")}


class OrganizationAccessList(ResourceAccessList):
    model = User  # needs to be User for AccessLists's
    parent_model = Organization


class OrganizationObjectRolesList(SubListAPIView):
    model = Role
    serializer_class = RoleSerializer
    parent_model = Organization
    search_fields = ('role_field', 'content_type__model')
    deprecated = True

    def get_queryset(self):
        po = self.get_parent_object()
        content_type = ContentType.objects.get_for_model(self.parent_model)
        return Role.objects.filter(content_type=content_type, object_id=po.pk)
