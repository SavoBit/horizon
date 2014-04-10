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

import re

from django.core import validators
from django.utils.translation import ugettext_lazy as _

from horizon import exceptions
from horizon import forms
from horizon import messages

from openstack_dashboard import api
from openstack_dashboard.dashboards.project.connections.mockobjects import ReachabilityTestStub
from openstack_dashboard.dashboards.project.connections.mockapi import ReachabilityTestAPI



NEW_LINES = re.compile(r"\r|\n")


class CreateReachabilityTest(forms.SelfHandlingForm):
    name = forms.CharField(max_length="255",
                           label=_("Name"),
                           required=True)
    connection_source = forms.ChoiceField(
	label=_('Connection Source'),
	required=True,
	choices=[('default',_(' ')),
		('vm1', _('VM 1')),
		('vm2', _('VM 2'))],
	widget=forms.Select(attrs={
		'class': 'switchable',
		'data-slug': 'source'}))

    connection_destination = forms.ChoiceField(
        label=_('Connection Destination'),
        required=True,
        choices=[('default',_(' ')),
                ('vm1', _('VM 1')),
		('vm2', _('VM 2'))],
        widget=forms.Select(attrs={
                'class': 'switchable',
                'data-slug': 'source'}))
    
    port = forms.CharField(max_length="255",
                           label=_("Port (optional)"),
                           required=False)

    port_protocol = forms.ChoiceField(
        label=_('Port Protocol (optional)'),
        required=False,
        choices=[('default',_('--- Select Protocol ---')),
		('tcp', _('TCP')),
                ('udp', _('UDP'))],
        widget=forms.Select(attrs={
                'class': 'switchable',
                'data-slug': 'source'}))

    expected_connection = forms.ChoiceField(
        label=_('Expected Connection Results'),
        required=True,
        choices=[('default',_('--- Select Result ---')),
                ('connect', _('Must Connect')),
                ('not_connect', _('Must Not Connect'))],
        widget=forms.Select(attrs={
                'class': 'switchable',
                'data-slug': 'source'}))

    
    def handle(self, request, data):
	test = ReachabilityTestStub(data['name'].encode('ascii','ignore'),'','')
	messages.success(request, _('Successfully created reachability test: %s') % data['name'])
	api = ReachabilityTestAPI()
	api.addReachabilityTest(test)
	#import pdb
        #pdb.set_trace()
        return test

