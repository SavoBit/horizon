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

from openstack_dashboard.utils import filters
from openstack_dashboard import api
from openstack_dashboard.dashboards.project.connections.mockobjects import ReachabilityTestStub
from openstack_dashboard.dashboards.project.connections.mockapi import ReachabilityTestAPI



NEW_LINES = re.compile(r"\r|\n")

class CreateReachabilityTest(forms.SelfHandlingForm):
    name = forms.CharField(max_length="255",
                           label=_("Name"),
                           required=True)

    connection_source_type = forms.ChoiceField(
        label=_('Connection Source Type'),
	required=True,
        widget=forms.Select(attrs={
                'class': 'switchable',
                'data-slug': 'connection_source_type'
	})
    )

    instance_source = forms.ChoiceField(
	label=_('Use instance as source'),
	required=True,
	widget=forms.Select(attrs={
		'class': 'switched',
		'data-switch-on': 'connection_source_type',
		'data-connection_source_type-instance': _('Use instance as source')}))

    ip_source = forms.CharField(max_length="255",
			  label=_("Use IP address as source"),
                          required=True,
                          initial="0.0.0.0/0",
                          widget=forms.TextInput(
                              attrs={'class': 'switched',
                                     'data-switch-on': 'connection_source_type',
                                     'data-connection_source_type-ip': _('Use IP address as source')}))

    mac_source = forms.CharField(max_length="255",
                           label=_("Use MAC address as source"),
			   initial="MAC Address",
                           required=True,
			   widget=forms.TextInput(attrs={
            			'class': 'switched',
            			'data-switch-on': 'connection_source_type',
            			'data-connection_source_type-mac': _('Use MAC address as source')}))

    connection_destination_type = forms.ChoiceField(
        label=_('Connection Destination Type'),
        required=True,
        widget=forms.Select(attrs={
                'class': 'switchable',
                'data-slug': 'connection_destination_type'}))

    instance_destination = forms.ChoiceField(
        label=_('Use instance as destination'),
        required=True,
        widget=forms.Select(attrs={
                'class': 'switched',
		'data-switch-on': 'connection_destination_type',
                'data-connection_destination_type-instance': _('Use instance as destination')}))

    ip_destination = forms.CharField(max_length="255",
			  label=_("Use IP address as destination"),
                          required=True,
                          initial="0.0.0.0/0",
                          widget=forms.TextInput(
                              attrs={'class': 'switched',
                                     'data-switch-on': 'connection_destination_type',
                                     'data-connection_destination_type-ip': _('Use IP address as destination')}))

    mac_destination = forms.CharField(max_length="255",
                           label=_("Use MAC address as destination"),
			   initial="MAC Address",
                           required=True,
                           widget=forms.TextInput(attrs={
                                'class': 'switched',
                                'data-switch-on': 'connection_destination_type',
                                'data-connection_destination_type-mac': _('Use MAC address as destination')}))

    expected_connection = forms.ChoiceField(
        label=_('Expected Connection Results'),
        required=True,
        choices=[('default',_('--- Select Result ---')),
                ('forward', _('Forward')),
                ('drop', _('Drop'))],
        widget=forms.Select(attrs={
                'class': 'switchable',
                'data-slug': 'expected_connection'}))

    def __init__(self, *args, **kwargs):
        super(CreateReachabilityTest, self).__init__(*args, **kwargs)
   	connection_type=[
		('default', _('--- Select Source Type ---')),
                ('instance', _('Instance')),
                ('ip', _('IP Address')),
                ('mac', _('MAC Address'))
        ]
	instance_list = [
		('default',_('--- Select Instance ---')),
                ('vm1', _('VM 1')),
                ('vm2', _('VM 2'))
	]
	self.fields['connection_source_type'].choices = connection_type
	connection_type[0] = ('default', _('--- Select Destination Type ---'))
	self.fields['connection_destination_type'].choices = connection_type
	self.fields['instance_source'].choices = instance_list
	self.fields['instance_destination'].choices = instance_list
	 
    def clean(self):
        cleaned_data = super(CreateReachabilityTest, self).clean()

        def update_cleaned_data(key, value):
            cleaned_data[key] = value
            self.errors.pop(key, None)
	
	#name = cleaned_data.get("name")
	#update_cleaned_data('name',name)

	#import pdb
	#pdb.set_trace()

	return cleaned_data

    def handle(self, request, data):
	test = ReachabilityTestStub(data['name'].encode('ascii','ignore'),'','')
	messages.success(request, _('Successfully created reachability test: %s') % data['name'])
	api = ReachabilityTestAPI()
	api.addReachabilityTest(test)
	#import pdb
        #pdb.set_trace()
        return test

class TroubleshootForm(forms.SelfHandlingForm):
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
        messages.success(request, _('Successfully ran quick test: %s') % data['name'])
        api = ReachabilityTestAPI()
        api.addQuickTest(test)
        #import pdb
        #pdb.set_trace()
        return test


class UpdateForm(forms.SelfHandlingForm):
    reachability_test_id = forms.CharField(widget=forms.HiddenInput())
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
        api = ReachabilityTestAPI()
        api.updateReachabilityTest(data['reachability_test_id'].encode('ascii','ignore'),test)
        #import pdb
        #pdb.set_trace()
	messages.success(request, _('Successfully updated reachability test.'))
        return test

