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

from django import conf
from django.utils.translation import ugettext_lazy as _

from horizon import tabs


"""Class to handle the data population of the test details views."""

class DetailsTab(tabs.Tab):
    name = _("Details")
    slug = "details"
    template_name = "project/connections/reachability_tests/_detail_overview.html"

    def get_context_data(self, request):
        reachability_test = self.tab_group.kwargs['reachability_test']
        return {"reachability_test": reachability_test}


class ReachabilityTestDetailTabs(tabs.TabGroup):
    slug = "reachability_test_details"
    tabs = (DetailsTab,)


class QuickDetailsTab(tabs.Tab):
    name = _("Quick Test Results")
    slug = "quick_details"
    template_name = "project/connections/reachability_tests/_quick_detail_overview.html"

    def get_context_data(self, request):
        quick_test = self.tab_group.kwargs['quick_test']
        return {"quick_test": quick_test}


class QuickTestDetailTabs(tabs.TabGroup):
    slug = "quick_test_details"
    tabs = (QuickDetailsTab,)
