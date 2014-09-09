# vim: tabstop=4 shiftwidth=4 softtabstop=4

# Copyright 2012 United States Government as represented by the
# Administrator of the National Aeronautics and Space Administration.
# All Rights Reserved.
#
# Copyright 2012 Nebula, Inc.
# Copyright 2012 OpenStack Foundation
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

import json

from django.utils.translation import ugettext_lazy as _

from horizon import exceptions
from horizon import forms
from horizon import messages
from horizon import tabs
from horizon import tables

from openstack_dashboard.api import keystone
from openstack_dashboard.api import network
from openstack_dashboard.api import nova

from openstack_dashboard.dashboards.project.connections.\
    top_talkers.tables import TopTalkersTable
from openstack_dashboard.dashboards.project.connections.\
    reachability_tests.tables import ReachabilityTestsTable
from openstack_dashboard.dashboards.project.connections.mockapi import NetworkTemplateAPI

from openstack_dashboard.dashboards.project.connections.reachability_tests.reachability_test_api import ReachabilityTestAPI
from openstack_dashboard.dashboards.project.connections.reachability_tests.reachability_test_db import \
     ReachabilityTest, ReachabilityTestResult, ReachabilityQuickTest, ReachabilityQuickTestResult
import openstack_dashboard.dashboards.project.connections.bsn_api as bsn_api
from openstack_dashboard.dashboards.project.connections.network_template \
    import network_template_api


class DeleteTemplateAction(tables.DeleteAction):
    data_type_singular = _("Network Template")
    data_type_plural = _("Network Templates")

    def delete(self, request, obj_id):
        network_template_api.delete_template_by_id(obj_id)


class CreateTemplateAction(tables.LinkAction):
    name = "create"
    verbose_name = _("Create Network Template")
    url = "horizon:admin:connections:network_template:create"
    classes = ("ajax-modal", "btn-create")


class NetworkTemplateAdminTable(tables.DataTable):
    template_id = tables.Column("id",
                                verbose_name=_("Template ID"))
    template_name = tables.Column(
        "template_name",
        link=("horizon:admin:connections:network_template:detail"),
        verbose_name=_("Template Name"))

    def get_object_id(self, template):
        return template.id

    class Meta:
        name = "networktemplate_admin"
        verbose_name = _("Network Template Administration")
        table_actions = (CreateTemplateAction, DeleteTemplateAction)
        row_actions = (DeleteTemplateAction,)


class NetworkTemplateAdminTab(tabs.TableTab):
    table_classes = (NetworkTemplateAdminTable,)
    name = _("Network Template Admin")
    slug = "network_template_tab_admin"
    template_name = "horizon/common/_detail_table.html"
    # TODO(kevinbenton): delete this file if not needed
    # template_name = "project/connections/network_template/_template_adminhome.html"

    def allowed(self, request):
        return (self.request.path.startswith('/admin/') and
                super(NetworkTemplateAdminTab, self).allowed(request))

    def get_networktemplate_admin_data(self):
        return network_template_api.get_network_templates()


class NetworkTemplateTab(tabs.Tab):
    name = _("Network Template")
    slug = "network_template_tab"
    template_name = "project/connections/network_template/_template_home.html"

    def allowed(self, request):
        # don't show the regular template tab to admins
        return (not request.path.startswith('/admin/')
                and super(NetworkTemplateTab, self).allowed(request))

    def get_context_data(self, request):
        return network_template_api.get_stack_topology(request)


class ReachabilityTestsTab(tabs.TableTab):
    table_classes = (ReachabilityTestsTable,)
    name = _("Reachability Tests")
    slug = "reachability_test_tab"
    template_name = "horizon/common/_detail_table.html"

    def get_reachability_tests_data(self):
        api = ReachabilityTestAPI()
        with bsn_api.Session.begin(subtransactions=True):
            reachability_tests = api.listReachabilityTests(
                self.request.user.project_id, bsn_api.Session)
        return reachability_tests


class TopTalkersTab(tabs.TableTab):
    table_classes = (TopTalkersTable,)
    name = _("Top Talkers")
    slug = "top_talkers_tab"
    template_name = "horizon/common/_detail_table.html"

    def get_toptalkers_data(self):
        # TODO(kevinbenton): Add an API call to get the data
        # to display for Top Talkers table.
        services = []
        return services


class ConnectionsTabs(tabs.TabGroup):
    slug = "connections_tabs"
    # TODO(kevinbenton): re-enabled top talkers once implemented
    # tabs = (NetworkTemplateTab, ReachabilityTestsTab, TopTalkersTab)
    sticky = True
    tabs = (ReachabilityTestsTab, NetworkTemplateTab, NetworkTemplateAdminTab)



class CreateNetworkTemplate(forms.SelfHandlingForm):
    name = forms.CharField(max_length=255, label=_("Name"), required=True)
    body = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 20}),
        max_length=None, label=_("Template Body"), required=True)
    existing_id = forms.CharField(widget=forms.HiddenInput(), required=False)
    template_name = "horizon/common/_detail_table.html"

    def handle(self, request, data):
        template = network_template_api.get_template_by_id(data['existing_id'])
        try:
            if template:
                network_template_api.update_template_by_id(
                    data['existing_id'], data['name'], data['body'])
            else:
                network_template_api.create_network_template(
                    data['name'], data['body'])
        except:
            messages.error(
                request, _("Unable to create template. "
                           "Verify that the name is unique."))
            return False
        messages.success(request, _("Template saved."))
        return True


class DetailNetworkTemplate(CreateNetworkTemplate):
    def __init__(self, request, *args, **kwargs):
        tid = request.path_info.split('/')[-1]
        template = network_template_api.get_template_by_id(tid)
        super(DetailNetworkTemplate, self).__init__(request, *args, **kwargs)
        if template:
            self.fields['existing_id'].initial = tid
            self.fields['name'].initial = template.template_name
            self.fields['body'].initial = template.body
