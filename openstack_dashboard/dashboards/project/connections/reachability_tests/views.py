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
Views for managing keypairs.
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

from openstack_dashboard import api

from openstack_dashboard.dashboards.project.connections.reachability_tests \
    import forms as project_forms


class CreateView(forms.ModalFormView):
    form_class = project_forms.CreateReachabilityTest
    template_name = 'project/connections/reachability_tests/create.html'
    success_url = reverse_lazy("horizon:project:connections:index")


class DownloadView(TemplateView):
    def get_context_data(self, reachability_test_name=None):
        return {'reachability_test_name': reachability_test_name}
    template_name = 'project/connections/reachability_tests/download.html'


class GenerateView(View):
    def get(self, request, reachability_test_name=None):
        try:
            reachability_test = api.nova.keypair_create(request, reachability_test_name)
        except Exception:
            redirect = reverse('horizon:project:connections:index')
            exceptions.handle(self.request,
                              _('Unable to create key pair: %(exc)s'),
                              redirect=redirect)

        response = http.HttpResponse(content_type='application/binary')
        response['Content-Disposition'] = \
                'attachment; filename=%s.pem' % slugify(reachability_test.name)
        response.write(reachability_test.private_key)
        response['Content-Length'] = str(len(response.content))
        return response
