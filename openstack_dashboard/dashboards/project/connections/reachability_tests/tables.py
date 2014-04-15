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


class DeleteReachabilityTests(tables.DeleteAction):
    data_type_singular = _("Test")
    data_type_plural = _("Tests")

    def delete(self, request, obj_id):
	#import pdb
        #pdb.set_trace()
	api = ReachabilityTestAPI()
        api.deleteReachabilityTest(obj_id.encode('ascii','ignore'))

class CreateReachabilityTest(tables.LinkAction):
    name = "create"
    verbose_name = _("Create Test")
    url = "horizon:project:connections:reachability_tests:create"
    classes = ("ajax-modal", "btn-create")

   # def allowed(self, request, reachability_test=None):
   #	import pdb
   #     pdb.set_trace()
   #     if reachability_test:
   #         return reachability_test.status == ''
   #     return True

class RunTroubleshootTest(tables.LinkAction):
    name = "troubleshoot"
    verbose_name = _("Run Test Now")
    url = "horizon:project:connections:reachability_tests:troubleshoot"
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
	api.runReachabilityTest(obj_id.encode('ascii','ignore'))
	#import pdb
        #pdb.set_trace()

class UpdateTest(tables.LinkAction):
    name = "update"
    verbose_name = _("Edit Test")
    url = "horizon:project:connections:reachability_tests:update"
    classes = ("ajax-modal", "btn-edit")
    #import pdb
    #pdb.set_trace()
    #def allowed(self, request, reachability_test=None):
    #	if not reachability_test:
    #		return True
    #	return reachability_test.name != 'default'

#class UpdateRow(tables.Row):
#    ajax = True

#    def get_data(self, request, reachability_test_id):
#	api = ReachabilityTestAPI()
#        reachability_test = api.getReachabilityTest(reachability_test_id.encode('ascii','ignore'))
	#import pdb
	#pdb.set_trace()
#        return reachability_test

def get_link_url(test):
    if test.last_run == '':
    	return ""
    else: 
	return "horizon:project:connections:reachability_tests:detail" 

def get_last_run(test):
    return getattr(test, "last_run", None) or test.last_run

def get_run_list(test):
    #import pdb
    #pdb.set_trace()
    api = ReachabilityTestAPI()
    #import pdb
    #pdb.set_trace()
    return api.listTestRuns(test.name)

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
	   		   #status=True,
			   status_choices=STATUS_CHOICES,
			   display_choices=STATUS_DISPLAY_CHOICES)
    run_list = tables.Column(get_run_list, hidden=True, verbose_name=_("Run List"))    
    #import pdb
    #pdb.set_trace()
   # def __init__
	#items = []
	#items.push(new ReachabilityTestStub("Test1");

    def get_object_id(self, reachability_test):
	#import pdb
	#pdb.set_trace()
        return reachability_test.name

    class Meta:
        name = "reachability_tests"
        verbose_name = _("Reachability Tests")
	#status_columns = ["status"]
	#row_class = UpdateRow
        table_actions = (CreateReachabilityTest, RunTroubleshootTest,  DeleteReachabilityTests, ReachabilityTestFilterAction)
        row_actions = (RunTest,UpdateTest,DeleteReachabilityTests)
