# Copyright 2014 Big Switch Networks
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

from openstack_dashboard.dashboards.project.connections.reachability_tests.\
    reachability_test_api import ReachabilityTestAPI
import openstack_dashboard.dashboards.project.connections.bsn_api as bsn_api


class DeleteReachabilityTests(tables.DeleteAction):
    data_type_singular = _("Test")
    data_type_plural = _("Tests")

    def delete(self, request, obj_id):
        api = ReachabilityTestAPI()
        with bsn_api.Session.begin(subtransactions=True):
            api.deleteReachabilityTest(request.user.tenant_id,
                                       obj_id.encode('ascii', 'ignore'),
                                       bsn_api.Session)


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
    classes = ("btn-edit", )

    def action(self, request, obj_id):
        api = ReachabilityTestAPI()
        with bsn_api.Session.begin(subtransactions=True):
            api.runReachabilityTest(request.user.tenant_id,
                                    obj_id.encode('ascii', 'ignore'),
                                    bsn_api.Session, request)


class UpdateTest(tables.LinkAction):
    name = "update"
    verbose_name = _("Edit Test")
    url = "horizon:project:connections:reachability_tests:update"
    classes = ("ajax-modal", "btn-edit")


def get_last_run(test):
    api = ReachabilityTestAPI()
    timestamp = None
    with bsn_api.Session.begin(subtransactions=True):
        last_result = api.getLastReachabilityTestResult(test.tenant_id,
                                                        test.test_id,
                                                        bsn_api.Session)
        if last_result:
            timestamp = last_result.test_time
    return timestamp


def get_status(test):
    api = ReachabilityTestAPI()
    status = ''
    with bsn_api.Session.begin(subtransactions=True):
        last_result = api.getLastReachabilityTestResult(test.tenant_id,
                                                        test.test_id,
                                                        bsn_api.Session)
        if last_result:
            status = last_result.test_result
    return status


def get_run_list(test):
    api = ReachabilityTestAPI()
    run_list = None
    with bsn_api.Session.begin(subtransactions=True):
        run_list = api.listReachabilityTestResults(test.tenant_id,
                                                   test.test_id,
                                                   bsn_api.Session)
    return run_list


STATUS_DISPLAY_CHOICES = (
    ("pass", _("PASS")),
    ("pending", _("PENDING")),
    ("fail", _("FAIL")),
    ("-", _("-")),
    ('', _("-")),
)

STATUS_CHOICES = (
    ("pass", True),
    ("-", None),
    ('', None),
    ("pending", None),
    ("fail", False),
)


class ReachabilityTestsTable(tables.DataTable):
    name = tables.Column("test_id", verbose_name=_("Test ID"))
    last_run = tables.Column(
        get_last_run,
        link=("horizon:project:connections:reachability_tests:detail"),
        verbose_name=_("Last Run")
    )
    status = tables.Column(
        get_status,
        filters=(title, filters.replace_underscores),
        verbose_name=_("Status"),
        status_choices=STATUS_CHOICES,
        display_choices=STATUS_DISPLAY_CHOICES
    )
    #hiddent column to store the data for the status list tool tip.
    run_list = tables.Column(get_run_list, hidden=True,
                             verbose_name=_("Run List"))

    def get_object_id(self, reachability_test):
        return reachability_test.test_id

    class Meta:
        name = "reachability_tests"
        verbose_name = _("Reachability Tests")
        table_actions = (CreateReachabilityTest, RunQuickTest,
                         DeleteReachabilityTests, ReachabilityTestFilterAction)
        row_actions = (RunTest, UpdateTest, DeleteReachabilityTests)
