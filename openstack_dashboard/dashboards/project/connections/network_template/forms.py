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

import netaddr

from django.conf import settings
from django.core.urlresolvers import reverse
from django.core import validators
from django.forms import ValidationError  # noqa
from django.utils.translation import ugettext_lazy as _

from horizon import exceptions
from horizon import forms
from horizon import messages
from horizon.utils import validators as utils_validators

from openstack_dashboard.utils import filters
from openstack_dashboard.dashboards.project.connections.mockapi \
    import NetworkTemplateAPI
from openstack_dashboard.dashboards.project.connections.mockobjects \
    import NetworkTemplateStub
from openstack_dashboard.dashboards.project.connections.network_template \
    import network_template_api
from openstack_dashboard.dashboards.project.connections import bsn_api

def findDefault(template_list, key):
    """Finds if a key exist within a dictionary.

    Returns empty string if not found.
    return: String
    """
    result = ''

    if key in template_list:
        result = template_list[key]

    return result


class SelectTemplateForm(forms.SelfHandlingForm):
    network_templates = forms.ChoiceField(
        label=_('Default Network Templates'),
        required=True,
    )

    def __init__(self, request, *args, **kwargs):
        super(SelectTemplateForm, self).__init__(request, *args, **kwargs)
        templates = network_template_api.get_network_templates()
        field_templates = []
        if templates:
            field_templates.append(
                ('default', _('--- Select Network Template ---')))
            for template in templates:
                field_templates.append(
                    (template.id, _(template.template_name)))
        else:
            field_templates.append(
                ('default', _('--- No Available Templates  ---')))
        self.fields['network_templates'].choices = field_templates

    def clean(self):
        cleaned_data = super(SelectTemplateForm, self).clean()

        def update_cleaned_data(key, value):
            cleaned_data[key] = value
            self.errors.pop(key, None)

        network_template = cleaned_data.get('network_templates')

        if network_template == 'default':
            msg = _('A template must be selected.')
            raise ValidationError(msg)
        record = network_template_api.get_template_by_id(network_template)
        if not record:
            msg = _('A template must be selected.')
            raise ValidationError(msg)
        return cleaned_data

    def handle(self, request, data):
        # nothing is done until the apply step because the required fields
        # need to be extracted.
        return data


class RemoveTemplateForm(forms.SelfHandlingForm):

    def handle(self, request, data):
        network_template_api.delete_associated_stack(request)
        return True


class ApplyTemplateForm(forms.SelfHandlingForm):
    failure_url = 'horizon:project:connections:index'

    def __init__(self, *args, **kwargs):
        super(ApplyTemplateForm, self).__init__(*args, **kwargs)
        try:
            template_id = self.request.path_info.split('/')[-1]
            template_db = network_template_api.get_template_by_id(template_id)
            if not template_db:
                raise Exception(_("Could not find a template with that ID."))
            if network_template_api.get_tenant_stack_assignment(
                    self.request.user.tenant_id):
                raise Exception(_("This tenant already has a deployed template."))
            if template_db:
                template = network_template_api.extract_fields_from_body(
                    self.request, template_db.body)
        except Exception as e:
            msg = _("Failed preparing template. You may not have permissions to "
                    "use Heat templates.")
            exceptions.handle(self.request, msg,
                              redirect=reverse(self.failure_url))

        # Sorts the parameters in the template.
        parameters = template['Parameters'].keys()
        parameters.sort()
        parameters.reverse()
        # Populates the form dynamically with information from the template.
        for parameter in parameters:
            self.fields[parameter] = forms.CharField(
                max_length="255",
                label=template['Parameters'][parameter]['Label'],
                initial=findDefault(template['Parameters'][parameter],
                                    'Default'),
                help_text=template['Parameters'][parameter]['Description'],
                required=True
            )

    def handle(self, request, data):
        try:
            template_id = self.request.path_info.split('/')[-1]
            template_db = network_template_api.get_template_by_id(template_id)
            if not template_db:
                raise Exception(_("Could not find a template with that ID."))
            if template_db:
                template = network_template_api.extract_fields_from_body(
                    self.request, template_db.body)
                hresource = network_template_api.deploy_instance(
                    self.request, template_db.id, data)
        except:
            msg = _("Error loading template")
            exceptions.handle(self.request, msg, redirect=self.failure_url)
        return True
