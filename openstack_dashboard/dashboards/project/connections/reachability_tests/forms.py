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
import time

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
			  label=_("Use ip address as source"),
                          required=True,
                          initial="0.0.0.0/0",
                          widget=forms.TextInput(
                              attrs={'class': 'switched',
                                     'data-switch-on': 'connection_source_type',
                                     'data-connection_source_type-ip': _('Use IP address as source')}))

    mac_source = forms.CharField(max_length="255",
                           label=_("Use mac address as source"),
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
			  label=_("Use ip address as destination"),
                          required=True,
                          initial="0.0.0.0/0",
                          widget=forms.TextInput(
                              attrs={'class': 'switched',
                                     'data-switch-on': 'connection_destination_type',
                                     'data-connection_destination_type-ip': _('Use IP address as destination')}))

    mac_destination = forms.CharField(max_length="255",
                           label=_("Use mac address as destination"),
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
	
        connection_source_type = cleaned_data.get('conection_source_type')
	connection_destination_type = cleaned_data.get('connection_destination_type')
	expected_connection = cleaned_data.get('expected_connection')	

	#Validation to check that default isn't selected.
	if connection_source_type == 'default':
		msg = _('A connection source type must be selected.')
		raise ValidationError(msg)
	if connection_destination_type == 'default':
		msg = _('A connection destination type must be selected.')
                raise ValidationError(msg)
	if expected_connection == 'default':
		msg = _('A expected connection result must be selected.')
                raise ValidationError(msg)

	return cleaned_data

    def handle(self, request, data):
	if data['connection_source_type'] == 'instance':
		source = data['instance_source'].encode('ascii','ignore')
		source_type = data['connection_source_type'].encode('ascii','ignore')
	elif data['connection_source_type'] == 'ip':
                source = data['ip_source'].encode('ascii','ignore')
		source_type = data['connection_source_type'].encode('ascii','ignore')
	elif data['connection_source_type'] == 'mac':
                source = data['mac_source'].encode('ascii','ignore')
		source_type = data['connection_source_type'].encode('ascii','ignore')

	if data['connection_destination_type'] == 'instance':
                dest = data['instance_destination'].encode('ascii','ignore')
		dest_type = data['connection_destination_type'].encode('ascii','ignore')
        elif data['connection_destination_type'] == 'ip':
                dest = data['ip_destination'].encode('ascii','ignore')
		dest_type = data['connection_destination_type'].encode('ascii','ignore')
        elif data['connection_destination_type'] == 'mac':
                dest = data['mac_destination'].encode('ascii','ignore')
		dest_type = data['connection_destination_type'].encode('ascii','ignore')

	expected = data['expected_connection'].encode('ascii','ignore')

	new_test_data = {'name' : data['name'].encode('ascii','ignore'),
			'connection_source_type' : source_type,
			'connection_source' : source,
			'connection_destination_type' : dest_type,
			'connection_destination' : dest,
			'expected_connection' : expected}

	#TODO: Replace with API call to create a test.
	test = ReachabilityTestStub(new_test_data)
        messages.success(request, _('Successfully created reachability test: %s') % data['name'])
        api = ReachabilityTestAPI()
        api.addReachabilityTest(test)

        return test

class RunQuickTestForm(forms.SelfHandlingForm):
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
			  label=_("Use ip address as source"),
                          required=True,
                          initial="0.0.0.0/0",
                          widget=forms.TextInput(
                              attrs={'class': 'switched',
                                     'data-switch-on': 'connection_source_type',
                                     'data-connection_source_type-ip': _('Use IP address as source')}))

    mac_source = forms.CharField(max_length="255",
                           label=_("Use mac address as source"),
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
			  label=_("Use ip address as destination"),
                          required=True,
                          initial="0.0.0.0/0",
                          widget=forms.TextInput(
                              attrs={'class': 'switched',
                                     'data-switch-on': 'connection_destination_type',
                                     'data-connection_destination_type-ip': _('Use IP address as destination')}))

    mac_destination = forms.CharField(max_length="255",
                           label=_("Use mac address as destination"),
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
        super(RunQuickTestForm, self).__init__(*args, **kwargs)
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
        cleaned_data = super(RunQuickTestForm, self).clean()

        def update_cleaned_data(key, value):
            cleaned_data[key] = value
            self.errors.pop(key, None)
	
        connection_source_type = cleaned_data.get('conection_source_type')
	connection_destination_type = cleaned_data.get('connection_destination_type')
	expected_connection = cleaned_data.get('expected_connection')	
	
	#Validation to check if that selection isn't default.
	if connection_source_type == 'default':
		msg = _('A connection source type must be selected.')
		raise ValidationError(msg)
	if connection_destination_type == 'default':
		msg = _('A connection destination type must be selected.')
                raise ValidationError(msg)
	if expected_connection == 'default':
		msg = _('A expected connection result must be selected.')
                raise ValidationError(msg)

	return cleaned_data


    def handle(self, request, data):

	if data['connection_source_type'] == 'instance':
                source = data['instance_source'].encode('ascii','ignore')
                source_type = data['connection_source_type'].encode('ascii','ignore')
        elif data['connection_source_type'] == 'ip':
                source = data['ip_source'].encode('ascii','ignore')
                source_type = data['connection_source_type'].encode('ascii','ignore')
        elif data['connection_source_type'] == 'mac':
                source = data['mac_source'].encode('ascii','ignore')
                source_type = data['connection_source_type'].encode('ascii','ignore')

        if data['connection_destination_type'] == 'instance':
                dest = data['instance_destination'].encode('ascii','ignore')
                dest_type = data['connection_destination_type'].encode('ascii','ignore')
        elif data['connection_destination_type'] == 'ip':
                dest = data['ip_destination'].encode('ascii','ignore')
                dest_type = data['connection_destination_type'].encode('ascii','ignore')
        elif data['connection_destination_type'] == 'mac':
                dest = data['mac_destination'].encode('ascii','ignore')
                dest_type = data['connection_destination_type'].encode('ascii','ignore')

	expected = data['expected_connection'].encode('ascii','ignore')

        new_test_data = {'name' : 'quick test',
                        'connection_source_type' : source_type,
                        'connection_source' : source,
                        'connection_destination_type' : dest_type,
                        'connection_destination' : dest,
                        'expected_connection' : expected}

	#TODO: Replace with API call to run a quick/troubleshoot test.
        test = ReachabilityTestStub(new_test_data) 
        api = ReachabilityTestAPI()
        api.addQuickTest(test)
	api.runQuickTest()
	test = api.getQuickTest()
	messages.success(request, _('Successfully ran quick test.'))

        return test


class UpdateForm(forms.SelfHandlingForm):
    reachability_test_id = forms.CharField(widget=forms.HiddenInput())

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
			  label=_("Use ip address as source"),
                          required=True,
                          initial="0.0.0.0/0",
                          widget=forms.TextInput(
                              attrs={'class': 'switched',
                                     'data-switch-on': 'connection_source_type',
                                     'data-connection_source_type-ip': _('Use IP address as source')}))

    mac_source = forms.CharField(max_length="255",
                           label=_("Use mac address as source"),
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
			  label=_("Use ip address as destination"),
                          required=True,
                          initial="0.0.0.0/0",
                          widget=forms.TextInput(
                              attrs={'class': 'switched',
                                     'data-switch-on': 'connection_destination_type',
                                     'data-connection_destination_type-ip': _('Use IP address as destination')}))

    mac_destination = forms.CharField(max_length="255",
                           label=_("Use mac address as destination"),
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
        super(UpdateForm, self).__init__(*args, **kwargs)
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
        cleaned_data = super(UpdateForm, self).clean()

        def update_cleaned_data(key, value):
            cleaned_data[key] = value
            self.errors.pop(key, None)
	
        connection_source_type = cleaned_data.get('conection_source_type')
	connection_destination_type = cleaned_data.get('connection_destination_type')
	expected_connection = cleaned_data.get('expected_connection')	

	#Validation to make sure the user make a selection.
	if connection_source_type == 'default':
		msg = _('A connection source type must be selected.')
		raise ValidationError(msg)
	if connection_destination_type == 'default':
		msg = _('A connection destination type must be selected.')
                raise ValidationError(msg)
	if expected_connection == 'default':
		msg = _('A expected connection result must be selected.')
                raise ValidationError(msg)

	return cleaned_data

    def handle(self, request, data):
	if data['connection_source_type'] == 'instance':
                source = data['instance_source'].encode('ascii','ignore')
                source_type = data['connection_source_type'].encode('ascii','ignore')
        elif data['connection_source_type'] == 'ip':
                source = data['ip_source'].encode('ascii','ignore')
                source_type = data['connection_source_type'].encode('ascii','ignore')
        elif data['connection_source_type'] == 'mac':
                source = data['mac_source'].encode('ascii','ignore')
                source_type = data['connection_source_type'].encode('ascii','ignore')

        if data['connection_destination_type'] == 'instance':
                dest = data['instance_destination'].encode('ascii','ignore')
                dest_type = data['connection_destination_type'].encode('ascii','ignore')
        elif data['connection_destination_type'] == 'ip':
                dest = data['ip_destination'].encode('ascii','ignore')
                dest_type = data['connection_destination_type'].encode('ascii','ignore')
        elif data['connection_destination_type'] == 'mac':
                dest = data['mac_destination'].encode('ascii','ignore')
                dest_type = data['connection_destination_type'].encode('ascii','ignore')	

	expected = data['expected_connection'].encode('ascii','ignore')

	new_test_data = {'name' : data['name'].encode('ascii','ignore'),
                        'connection_source_type' : source_type,
                        'connection_source' : source,
                        'connection_destination_type' : dest_type,
                        'connection_destination' : dest,
                        'expected_connection' : expected}
       
	#TODO: Replace with API call to update an existing test with new data. 
	test = ReachabilityTestStub(new_test_data)
        api = ReachabilityTestAPI()
        api.updateReachabilityTest(data['reachability_test_id'].encode('ascii','ignore'),test)
        messages.success(request, _('Successfully updated reachability test.'))

        return test


class SaveQuickTestForm(forms.SelfHandlingForm):
    name = forms.CharField(max_length="255",
                           label=_("Name"),
                           required=True)

    def __init__(self, *args, **kwargs):
        super(SaveQuickTestForm, self).__init__(*args, **kwargs)

    def clean(self):
        cleaned_data = super(SaveQuickTestForm, self).clean()

        def update_cleaned_data(key, value):
            cleaned_data[key] = value
            self.errors.pop(key, None)

        return cleaned_data

    def handle(self, request, data):
	#TODO: Replace with API call to save a quick/troubleshoot test
	api = ReachabilityTestAPI()
        test = api.saveQuickTest(data['name'].encode('ascii','ignore'))
        messages.success(request, _('Successfully saved quick test: %s') % data['name'])
        
	return test
