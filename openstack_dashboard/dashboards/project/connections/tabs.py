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
from horizon import messages
from horizon import tabs

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
import openstack_dashboard.dashboards.project.connections.reachability_tests.const as const

class NetworkTemplateTab(tabs.Tab):
    name = _("Network Template")
    slug = "network_template_tab"
    template_name = "project/connections/network_template/_template_home.html"
   
    def get_context_data(self,request):
	#TODO: Replace with API call to get the current template applied.
	#This will be used to render the page.
	api = NetworkTemplateAPI()
	template = api.getHeatTemplate()

	if(template.has_key('web_map')):
		entities = json.dumps(template['web_map'].network_entities)
		connections = json.dumps(template['web_map'].network_connections)
	else:
		entities = {}
		connections = {}

	return {"network_entities": entities, "network_connections": connections}


class ReachabilityTestsTab(tabs.TableTab):
    table_classes = (ReachabilityTestsTable,)
    name = _("Reachability Tests")
    slug = "reachability_test_tab"
    template_name = "horizon/common/_detail_table.html"

    def get_reachability_tests_data(self):
        api = ReachabilityTestAPI()
        session = const.Session()
        with session.begin(subtransactions=True):
	    reachability_tests = api.listReachabilityTests(const.tenant_id, session)
        return reachability_tests

class TopTalkersTab(tabs.TableTab):
    table_classes = (TopTalkersTable,)
    name = _("Top Talkers")
    slug = "top_talkers_tab"
    template_name = "horizon/common/_detail_table.html"

    def get_toptalkers_data(self):
	#TODO: Add an API call to get the data to display for Top Talkers table.
        services = []
        return services


class ConnectionsTabs(tabs.TabGroup):
    slug = "connections_tabs"
    tabs = (NetworkTemplateTab, ReachabilityTestsTab, TopTalkersTab)
    sticky = True
