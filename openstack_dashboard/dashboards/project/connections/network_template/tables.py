# vim: tabstop=4 shiftwidth=4 softtabstop=4

# Copyright 2012 Nebula, Inc.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

from django.utils.translation import string_concat  # noqa
from django.utils.translation import ugettext_lazy as _
from django.template.defaultfilters import title

from horizon import tables
from horizon.utils import filters

from openstack_dashboard import api
from openstack_dashboard.usage import quotas
from openstack_dashboard.dashboards.project.connections.mockapi import ReachabilityTestAPI
from openstack_dashboard.dashboards.project.connections.mockobjects import ReachabilityTestStub


class ApplyTemplate(tables.LinkAction):
    name = "apply_template"
    verbose_name = _("Apply Network Template")
    url = "horizon:project:connections:network_template:apply_template"
    classes = ("ajax-modal", "btn-create")


class RemoveTemplate(tables.DeleteAction):
    data_type_singular = _("Template")
    data_type_plural = _("Templates")

    def delete(self, request, obj_id):
	return 0

class NetworkTemplateTable(tables.DataTable):
    name = tables.Column("name", hidden=True,
                              verbose_name=_("Name"))

    def get_object_id(self, network_template):
	return network_template.name

    class Meta:
        name = "network_templates"
        verbose_name = _("Network Template")
        table_actions = (ApplyTemplate, RemoveTemplate)
