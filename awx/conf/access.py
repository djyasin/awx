# Copyright (c) 2016 Ansible, Inc.
# All Rights Reserved.

# IMPORTANT: Platform Auditor changes for AAP 2.5 ONLY - DO NOT FORWARD PORT TO 2.6+
# This change enables Platform Auditor access to settings endpoints by using the
# is_auditor convenience property instead of only checking is_system_auditor
# AIA: Platform Auditor support added to settings access (lines 16, 29, 35)
# AIA PAI Nc Hin R Claude Code - https://aiattribution.github.io/interpret-attribution

# Django
from django.db.models import Q

# AWX
from awx.main.access import BaseAccess, register_access
from awx.conf.models import Setting


class SettingAccess(BaseAccess):
    """
    - I can see settings when I am a super user or auditor (system or platform).
    - I can edit settings when I am a super user.
    - I can clear settings when I am a super user.
    - I can always see/edit/clear my own user settings.

    NOTE: Platform Auditor support added for AAP 2.5 only via is_auditor property
    """

    model = Setting

    # For the checks below, obj will be an instance of a "Settings" class with
    # an attribute for each setting and a "user" attribute (set to None unless
    # it is a user setting).

    def get_queryset(self):
        # AAP 2.5 ONLY - DO NOT FORWARD PORT: Changed from is_system_auditor to is_auditor for Platform Auditor support
        if self.user.is_superuser or self.user.is_auditor:
            return self.model.objects.filter(Q(user__isnull=True) | Q(user=self.user))
        else:
            return self.model.objects.filter(user=self.user)

    def can_read(self, obj):
        # AAP 2.5 ONLY - DO NOT FORWARD PORT: Changed from is_system_auditor to is_auditor for Platform Auditor support
        return bool(self.user.is_superuser or self.user.is_auditor or (obj and obj.user == self.user))

    def can_add(self, data):
        return False  # There is no API endpoint to POST new settings.

    def can_change(self, obj, data):
        return bool(self.user.is_superuser or (obj and obj.user == self.user))

    def can_delete(self, obj):
        return bool(self.user.is_superuser or (obj and obj.user == self.user))


register_access(Setting, SettingAccess)
