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
from openstack_dashboard.dashboards.project.connections.mockobjects import ReachabilityTestStub


def findDefault(template_list,key):
	#import pdb
	#pdb.set_trace()
	result = ''
	if template_list.has_key(key):
		result = template_list[key]
	#import pdb
	#pdb.set_trace()
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
                ('template1', _('Template 1')),
                ('template2', _('Template 2')),
                ('tempalte3', _('Tempalte 3'))
        ]
	self.fields['network_templates'].choices = templates
	
	#import pdb
	#pdb.set_trace()


    def handle(self, request, data):
	#import pdb
	#pdb.set_trace()
	return data

class ApplyTemplateForm(forms.SelfHandlingForm):
    

    def __init__(self, *args, **kwargs):
        super(ApplyTemplateForm, self).__init__(*args, **kwargs)
	
	api = NetworkTemplateAPI()
	api.loadHeatTemplate()
        template = api.getHeatTemplate()
        #import pdb
        #pdb.set_trace()
        for parameter in template['parameters']:
                #import pdb
                #pdb.set_trace()
                self.fields[parameter] = forms.CharField(max_length ="255",
                                                        label=_(template['parameters'][parameter]['label']),
                                                        initial=findDefault(template['parameters'][parameter],'default'),
                                                        help_text=_(template['parameters'][parameter]['description']),
                                                        required=True)

        #import pdb
        #pdb.set_trace()



    def handle(self, request, data):
        #import pdb
        #pdb.set_trace()
        return True
