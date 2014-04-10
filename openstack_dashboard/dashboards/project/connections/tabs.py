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

from django.utils.translation import ugettext_lazy as _

from horizon import exceptions
from horizon import messages
from horizon import tabs

from openstack_dashboard.api import keystone
from openstack_dashboard.api import network
from openstack_dashboard.api import nova

from openstack_dashboard.dashboards.project.connections.\
    top_talkers.tables import TopTalkersTable
from openstack_dashboard.dashboards.project.connections.\
    reachability_tests.tables import ReachabilityTestsTable
from openstack_dashboard.dashboards.project.connections.mockdata import ReachabilityTestStub


class NetworkTemplateTab(tabs.Tab):
    name = _("Network Template")
    slug = "network_template_tab"
    template_name = "horizon/common/_detail_table.html"
   
    def get_context_data(self,request):
	return None

class ReachabilityTestsTab(tabs.TableTab):
    table_classes = (ReachabilityTestsTable,)
    name = _("Reachability Tests")
    slug = "reachability_test_tab"
    template_name = "horizon/common/_detail_table.html"

    def get_reachability_tests_data(self):
        try:
            reachability_tests = [ReachabilityTestStub('Test1','',''),ReachabilityTestStub('Test2','',''),ReachabilityTestStub('Test3','','')]
	    #import pdb
	    #pdb.set_trace()
        except Exception:
            reachability_tests = []
            exceptions.handle(self.request,
                              _('Unable to retrieve reachability test list.'))
        return reachability_tests


class TroubleshootTab(tabs.Tab):
    name = _("Troubleshoot")
    slug = "troubleshoot_tab"
    template_name = "horizon/common/_detail_table.html"
        
    def get_context_data(self,request):
	return None


class TopTalkersTab(tabs.TableTab):
    table_classes = (TopTalkersTable,)
    name = _("Top Talkers")
    slug = "top_talkers_tab"
    template_name = "horizon/common/_detail_table.html"

    def get_toptalkers_data(self):
        services = []
        for i, service in enumerate(self.request.user.service_catalog):
            service['id'] = i
            services.append(
                keystone.Service(service, self.request.user.services_region))

        return services


class ConnectionsTabs(tabs.TabGroup):
    slug = "connections_tabs"
    tabs = (NetworkTemplateTab, ReachabilityTestsTab, TroubleshootTab, TopTalkersTab)
    sticky = True
