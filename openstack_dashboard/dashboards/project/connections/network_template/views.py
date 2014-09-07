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
Views for managing instances.
"""
from django.core.urlresolvers import reverse
from django.core.urlresolvers import reverse_lazy
# from django.utils.translation import ugettext_lazy as _

# from horizon import exceptions
from horizon import forms
# from horizon import tables
# from horizon.utils import memoized

# from openstack_dashboard import api
# from openstack_dashboard.utils import filters

from openstack_dashboard.dashboards.project.connections.\
    network_template import forms as project_forms
from openstack_dashboard.dashboards.project.connections \
    import tabs as project_tabs


class ApplyTemplateView(forms.ModalFormView):
    form_class = project_forms.ApplyTemplateForm
    template_name = 'project/connections/network_template/apply_template.html'
    success_url = reverse_lazy('horizon:project:connections:index')

    def get_context_data(self, **kwargs):
        context = super(ApplyTemplateView, self).get_context_data(**kwargs)
        context['template_id'] = self.request.path_info.split('/')[-1]
        return context

class PopulateTemplateView(forms.ModalFormView):
    form_class = project_forms.ApplyTemplateForm
    template_name = 'project/connections/network_template/temp_page.html'

    def get_context_data(self, **kwargs):
        context = super(PopulateTemplateView, self).get_context_data(**kwargs)
        context['template_id'] = self.request.path_info.split('/')[-1]
        return context


class SelectTemplateView(forms.ModalFormView):
    form_class = project_forms.SelectTemplateForm
    template_name = 'project/connections/network_template/select_template.html'
    success_url = (
        'horizon:project:connections:network_template:populate_template')

    def get_success_url(self):
        return reverse(
            self.success_url,
            kwargs={'template_id': self.request.POST['network_templates']})


class RemoveTemplateView(forms.ModalFormView):
    form_class = project_forms.RemoveTemplateForm
    template_name = 'project/connections/network_template/remove_template.html'
    success_url = reverse_lazy('horizon:project:connections:index')


class CreateView(forms.ModalFormView):
    form_class = project_tabs.CreateNetworkTemplate
    success_url = reverse_lazy('horizon:admin:connections:index')
    template_name = 'project/connections/network_template/admin_create.html'


class DetailView(forms.ModalFormView):
    form_class = project_tabs.DetailNetworkTemplate
    success_url = reverse_lazy('horizon:admin:connections:index')
    template_name = 'project/connections/network_template/admin_create.html'
