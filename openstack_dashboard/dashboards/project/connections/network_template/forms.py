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
from horizon.utils import fields
from horizon.utils import validators as utils_validators

from openstack_dashboard import api
from openstack_dashboard.utils import filters
from openstack_dashboard.dashboards.project.connections.mockapi import NetworkTemplateAPI
from openstack_dashboard.dashboards.project.connections.mockobjects import NetworkTemplateStub

"""Finds if a key exist within a dictionary. Returns empty
   string if not found.
   return: String"""
def findDefault(template_list,key):
	result = ''

	if template_list.has_key(key):
		result = template_list[key]

	return result

class SelectTemplateForm(forms.SelfHandlingForm):
    network_templates = forms.ChoiceField(
        label=_('Default Network Templates'),
        required=True,
        )
    
    def __init__(self, *args, **kwargs):
        super(SelectTemplateForm, self).__init__(*args, **kwargs)
        templates=[
                ('default', _('--- Select Network Template ---')),
                ('template1', _('Template 1'))
        ]
	self.fields['network_templates'].choices = templates
	
    def clean(self):
        cleaned_data = super(SelectTemplateForm, self).clean()

        def update_cleaned_data(key, value):
            cleaned_data[key] = value
            self.errors.pop(key, None)

        network_template = cleaned_data.get('network_templates')

        if network_template == 'default':
                msg = _('A template must be selected.')
                raise ValidationError(msg)

        return cleaned_data
    
    def handle(self, request, data):
	#TODO: Replace the following lines with your API call to load templates.
	api = NetworkTemplateAPI()
	api.loadHeatTemplate()

	return data


class RemoveTemplateForm(forms.SelfHandlingForm):

    def __init__(self, *args, **kwargs):
        super(RemoveTemplateForm, self).__init__(*args, **kwargs)

    def handle(self, request, data):
	#TODO: Replace the following with your API call to remove template.
        api = NetworkTemplateAPI()
        api.removeHeatTemplate()

        return True


class ApplyTemplateForm(forms.SelfHandlingForm):
    
    def __init__(self, *args, **kwargs):
        super(ApplyTemplateForm, self).__init__(*args, **kwargs)
	
	#TODO: Replace with your API call to load the selected template.
	api = NetworkTemplateAPI()
        template = api.getHeatTemplate()

	#Sorts the parameters in the template.
	parameters = template['parameters'].keys()
	parameters.sort()
	parameters.reverse()

	#Populates the form dynamically with information from the template.
        for parameter in parameters:
                self.fields[parameter] = forms.CharField(max_length ="255",
                                                        label=_(template['parameters'][parameter]['label']),
                                                        initial=findDefault(template['parameters'][parameter],'default'),
                                                        help_text=_(template['parameters'][parameter]['description']),
                                                        required=True)

    def handle(self, request, data):
	#TODO: Replace with your own API call to fetch the current template.
	api = NetworkTemplateAPI()
	template = api.getHeatTemplate()

	new_data = {}
	new_data = template['resources']
	network_entities = {}
	network_connections = {}

	#Fetches the data entered in the form and populates a dictionary based of it and of the networks available.
	for resource in template['resources']:
		if(new_data[resource].has_key('properties')):
			if(new_data[resource]['properties'].has_key('name')):
				network_entities[resource] = {'properties':{'name':''}}
				network_entities[resource]['properties']['name'] = data[new_data[resource]['properties']['name']['get_param']].encode('ascii','ignore')
	
	#Fetches information from the template and makes a connections mapping. 
	#TODO: The mapping is based of name. Change if name changes or using a different way to represent connecitons in the template.
	for network in network_entities:
		token = network.split("_")
		if(token[0] == "out"):
			if(network_entities.has_key('mid_net')):
				network_connections[network] = {'destination' : 'mid_net', 'expected_connection' : 'forward'}
		elif(token[0] == "mid"):
			if(network_entities.has_key('inner_net')):
				network_connections[network] = {'destination' : 'inner_net', 'expected_connection' : 'forward'}
	
	#Create new object to hold the to dictionaries.
	network_template = NetworkTemplateStub({"network_entities" : network_entities, "network_connections" : network_connections})
	template['web_map'] = network_template
	api.updateHeatTemplate(template)

        return template
