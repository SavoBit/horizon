# vim: tabstop=4 shiftwidth=4 softtabstop=4

# Copyright 2012 United States Government as represented by the
# Administrator of the National Aeronautics and Space Administration.
# All Rights Reserved.
#
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

"""
Views for managing reachability test.
"""
from django.core.urlresolvers import reverse
from django.core.urlresolvers import reverse_lazy
from django import http
from django.template.defaultfilters import slugify  # noqa
from django.utils.translation import ugettext_lazy as _
from django.views.generic import TemplateView  # noqa
from django.views.generic import View  # noqa

from horizon import exceptions
from horizon import forms
from horizon.utils import memoized
from horizon import tabs

from openstack_dashboard import api
from openstack_dashboard.dashboards.project.connections.reachability_tests \
    import forms as project_forms
from openstack_dashboard.dashboards.project.connections.reachability_tests \
    import tabs as project_tabs
from openstack_dashboard.dashboards.project.connections.reachability_tests.reachability_test_api import ReachabilityTestAPI
from openstack_dashboard.dashboards.project.connections.reachability_tests.reachability_test_db \
    import ReachabilityTest, ReachabilityTestResult, ReachabilityQuickTest, ReachabilityQuickTestResult, tenant_id, Session


class CreateView(forms.ModalFormView):
    form_class = project_forms.CreateReachabilityTest
    template_name = 'project/connections/reachability_tests/create.html'
    success_url = reverse_lazy("horizon:project:connections:index")


class RunQuickTestView(forms.ModalFormView):
    form_class = project_forms.RunQuickTestForm
    template_name = 'project/connections/reachability_tests/quick_test.html'
    success_url = reverse_lazy("horizon:project:connections:reachability_tests:quick")


class UpdateView(forms.ModalFormView):
    form_class = project_forms.UpdateForm
    template_name = 'project/connections/reachability_tests/update.html'
    success_url = reverse_lazy('horizon:project:connections:index')

    @memoized.memoized_method
    def get_object(self):
        test = None
        try:
	    api = ReachabilityTestAPI()
            session = Session()
            test = api.getReachabilityTest(tenant_id, self.kwargs['reachability_test_id'].encode('ascii','ignore'), session)
            session.commit()
        except Exception:
            session.rollback()
            msg = _('Unable to retrieve test.')
            url = reverse('horizon:project:connections:index')
            exceptions.handle(self.request, msg, redirect=url)
        finally:
            session.close()
        return test

    def get_context_data(self, **kwargs):
        context = super(UpdateView, self).get_context_data(**kwargs)
        context['reachability_test'] = self.get_object()
        return context

    def get_initial(self):
        reachability_test = self.get_object()
        properties = getattr(reachability_test, 'properties', {})
	
        return {'reachability_test_id': self.kwargs['reachability_test_id'],
		connection_source : reachability_test.connection_source,
		connection_destination : reachability_test.connection_destination,
                'name': reachability_test.name,
		'expected_connection' : reachability_test.expected_connection}


class DetailView(tabs.TabView):
    tab_group_class = project_tabs.ReachabilityTestDetailTabs
    template_name = 'project/connections/reachability_tests/detail.html'

    def get_context_data(self, **kwargs):
        context = super(DetailView, self).get_context_data(**kwargs)
        context["reachability_test"] = self.get_data()
        return context

    @memoized.memoized_method
    def get_data(self):
        test = None
        try:
            api = ReachabilityTestAPI()
            session = Session()
            test = api.getReachabilityTest(tenant_id, self.kwargs['reachability_test_id'].encode('ascii','ignore'), session)
            session.commit()
        except Exception:
            session.rollback()
            url = reverse('horizon:project:connections:index')
            exceptions.handle(self.request,
                              _('Unable to retrieve reachability test details.'),
                              redirect=url)
        finally:
            session.close()
        return test

    def get_tabs(self, request, *args, **kwargs):
        reachability_test = self.get_data()
        return self.tab_group_class(request, reachability_test=reachability_test, **kwargs)


class QuickDetailView(tabs.TabView):
    tab_group_class = project_tabs.QuickTestDetailTabs
    template_name = 'project/connections/reachability_tests/quick_detail.html'

    def get_context_data(self, **kwargs):
        context = super(QuickDetailView, self).get_context_data(**kwargs)
        context["quick_test"] = self.get_data()

        return context

    @memoized.memoized_method
    def get_data(self):
        test = None
        try:
            api = ReachabilityTestAPI()
            session = Session()
            test = api. getQuickTest(tenant_id, session)
            session.commit()
        except Exception:
            session.rollback()
            url = reverse('horizon:project:connections:index')
            exceptions.handle(self.request,
                              _('Could not run quick test.'),
                              redirect=url)
        finally:
            session.close()
        return test

    def get_tabs(self, request, *args, **kwargs):
        quick_test = self.get_data()
        return self.tab_group_class(request, quick_test=quick_test, **kwargs)


class SaveQuickTestView(forms.ModalFormView):
    form_class = project_forms.SaveQuickTestForm
    template_name = 'project/connections/reachability_tests/save.html'
    success_url = reverse_lazy("horizon:project:connections:index")
