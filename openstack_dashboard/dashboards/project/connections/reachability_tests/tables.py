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

from openstack_dashboard.dashboards.project.connections.reachability_tests.reachability_test_api import ReachabilityTestAPI
from openstack_dashboard.dashboards.project.connections.reachability_tests.reachability_test_db \
      import ReachabilityTest, ReachabilityTestResult, ReachabilityQuickTest, ReachabilityQuickTestResult, tenant_id, Session

class DeleteReachabilityTests(tables.DeleteAction):
    data_type_singular = _("Test")
    data_type_plural = _("Tests")

    def delete(self, request, obj_id):
	api = ReachabilityTestAPI()
        session = Session()
        with session.begin(subtransactions=True):
            api.deleteReachabilityTest(tenant_id, obj_id.encode('ascii','ignore'), session)

class CreateReachabilityTest(tables.LinkAction):
    name = "create"
    verbose_name = _("Create Test")
    url = "horizon:project:connections:reachability_tests:create"
    classes = ("ajax-modal", "btn-create")


class RunQuickTest(tables.LinkAction):
    name = "quick_test"
    verbose_name = _("Quick Test")
    url = "horizon:project:connections:reachability_tests:run"
    classes = ("ajax-modal", "btn-edit")


class ReachabilityTestFilterAction(tables.FilterAction):
    
    def filter(self, table, reachability_tests, filter_string):
	"""Naive case-insentitive search."""
	q = filter_string.lower()
	return [reachability_test for reachability_test in reachability_tests
		if q in reachability_tests.name.lower()]


class RunTest(tables.BatchAction):
    name = "run"
    action_present = _("Run")
    action_past = _("Running")
    data_type_singular = _("Test")
    classes = ("btn-edit",)
        
    def action(self, request, obj_id):
	api = ReachabilityTestAPI()
	session = Session()
        with session.begin(subtransactions=True):
            api.runReachabilityTest(tenant_id, obj_id.encode('ascii','ignore'), session)

class UpdateTest(tables.LinkAction):
    name = "update"
    verbose_name = _("Edit Test")
    url = "horizon:project:connections:reachability_tests:update"
    classes = ("ajax-modal", "btn-edit")


def get_last_run(test):
    return getattr(test, "last_run", None) or test.last_run


def get_run_list(test):
    api = ReachabilityTestAPI()
    session = Session()
    with session.begin(subtransactions=True):
        api.listReachabilityTestResults(tenant_id, test.name, session)

STATUS_DISPLAY_CHOICES = (
    ("pass", _("PASS")),
    ("pending", _("PENDING")),
    ("fail", _("FAIL")),
    ("-", _("-")),
    ('', _("-")),
)


class ReachabilityTestsTable(tables.DataTable):
    STATUS_CHOICES = (
	("pass", True),
	("-", None),
	('', None),
	("pending", None),
	("fail", False),
    )
    name = tables.Column("name", verbose_name=_("Name"))
    last_run = tables.Column(get_last_run, link=("horizon:project:connections:reachability_tests:detail"), verbose_name=_("Last Run"))
    status = tables.Column("status", 
			   filters=(title, filters.replace_underscores), 
			   verbose_name=_("Status"),
			   status_choices=STATUS_CHOICES,
			   display_choices=STATUS_DISPLAY_CHOICES)
    #hiddent column to store the data for the status list tool tip.
    run_list = tables.Column(get_run_list, hidden=True, verbose_name=_("Run List"))    

    def get_object_id(self, reachability_test):
        return reachability_test.name

    class Meta:
        name = "reachability_tests"
        verbose_name = _("Reachability Tests")
        table_actions = (CreateReachabilityTest, RunQuickTest,  DeleteReachabilityTests, ReachabilityTestFilterAction)
        row_actions = (RunTest,UpdateTest,DeleteReachabilityTests)
