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
from openstack_dashboard.dashboards.project.connections.reachability_tests.reachability_test_api import ReachabilityTestAPI
from openstack_dashboard.dashboards.project.connections.reachability_tests.reachability_test_db import \
     ReachabilityTest, ReachabilityTestResult, ReachabilityQuickTest, ReachabilityQuickTestResult, tenant_id, Session

NEW_LINES = re.compile(r"\r|\n")
EXPECTATION_CHOICES = [('default',_('--- Select Result ---')),\
                       ('reached destination', _('reached destination')),\
                       ('dropped by route', _('dropped by route')),\
                       ('dropped by policy', _('dropped by policy')),
                       ('dropped due to private segment', _('dropped due to private segment')),
                       ('packet in', _('packet in')),
                       ('forwared', _('forwared')),
                       ('dropped', _('dropped')),
                       ('multiple sources', _('multiple sources')),
                       ('unsupported', _('unsupported')),\
                       ('invalid input', _('invalid input'))]

class CreateReachabilityTest(forms.SelfHandlingForm):

    name = forms.CharField(max_length="255",
                           label=_("Name"),
                           required=True)

    tenant_source = forms.CharField(max_length="255",
                          label=_("Sepecify source tenant"),
                          required=True,
                          initial="",
                          widget=forms.TextInput(
                              attrs={'class': 'switched',
                                     'data-connection_source-tenant': _('Specify source tenant')}))

    segment_source = forms.CharField(max_length="255",
                          label=_("Sepecify source segment"),
                          required=True,
                          initial="",
                          widget=forms.TextInput(
                              attrs={'class': 'switched',
                                     'data-connection_source-segment': _('Specify source segment')}))

    ip_source = forms.CharField(max_length="255",
			  label=_("Use ip address as source"),
                          required=True,
                          initial="0.0.0.0",
                          widget=forms.TextInput(
                              attrs={'class': 'switched',
                                     'data-connection_source_type-ip': _('Specify source IP address')}))

    tenant_destination = forms.CharField(max_length="255",
                          label=_("Sepecify destination tenant"),
                          required=True,
                          initial="",
                          widget=forms.TextInput(
                              attrs={'class': 'switched',
                                     'data-connection_destination-tenant': _('Specify destination tenant')}))

    segment_destination = forms.CharField(max_length="255",
                          label=_("Sepecify destination segment"),
                          required=True,
                          initial="",
                          widget=forms.TextInput(
                              attrs={'class': 'switched',
                                     'data-connection_destination-segment': _('Specify destination segment')}))

    ip_destination = forms.CharField(max_length="255",
			  label=_("Use ip address as destination"),
                          required=True,
                          initial="0.0.0.0",
                          widget=forms.TextInput(
                              attrs={'class': 'switched',
                                     'data-connection_destination_type-ip': _('Specify destination IP address')}))

    expected_connection = forms.ChoiceField(
        label=_('Expected Connection Results'),
        required=True,
        choices=EXPECTATION_CHOICES,
        widget=forms.Select(attrs={
                'class': 'switchable',
                'data-slug': 'expected_connection'}))

    def __init__(self, *args, **kwargs):
        super(CreateReachabilityTest, self).__init__(*args, **kwargs)

    def clean(self):
        cleaned_data = super(CreateReachabilityTest, self).clean()

        def update_cleaned_data(key, value):
            cleaned_data[key] = value
            self.errors.pop(key, None)
	
	expected_connection = cleaned_data.get('expected_connection')	

	if expected_connection == 'default':
		msg = _('A expected connection result must be selected.')
                raise ValidationError(msg)

	return cleaned_data

    def handle(self, request, data):
        test_id = data['name'].encode('ascii','ignore')
        source = {}
        source['tenant'] = data['tenant_source'].encode('ascii')
        source['segment'] = data['segment_source'].encode('ascii')
        source['ip'] = data['ip_source'].encode('ascii','ignore')
        dest = {}
        dest['tenant'] = data['tenant_destination'].encode('ascii')
        dest['segment'] = data['segment_destination'].encode('ascii')
        dest['ip'] = data['ip_destination'].encode('ascii','ignore')
	expected = data['expected_connection'].encode('ascii','ignore')
	new_test_data = {'name' : test_id,
			'connection_source' : source,
			'connection_destination' : dest,
			'expected_connection' : expected}

        test = ReachabilityTest(tenant_id = tenant_id,\
                                test_id = test_id,\
                                src_tenant_id = source['tenant'],\
                                src_segment_id = source['segment'],\
                                src_ip = source['ip'],\
                                dst_tenant_id = dest['tenant'],\
                                dst_segment_id = dest['segment'],\
                                dst_ip = dest['ip'],\
                                expected_result = expected)
        api = ReachabilityTestAPI()
        session = Session()
        try:
            test = api.addReachabilityTest(test, session)
            session.commit()
        except:
            session.rollback()
            raise
        finally:
            session.close()
        messages.success(request, _('Successfully created reachability test: %s') % data['name'])
        return test

class RunQuickTestForm(forms.SelfHandlingForm):

    tenant_source = forms.CharField(max_length="255",
                          label=_("Sepecify source tenant"),
                          required=True,
                          initial="",
                          widget=forms.TextInput(
                              attrs={'class': 'switched',
                                     'data-connection_source-tenant': _('Specify source tenant')}))

    segment_source = forms.CharField(max_length="255",
                          label=_("Sepecify source segment"),
                          required=True,
                          initial="",
                          widget=forms.TextInput(
                              attrs={'class': 'switched',
                                     'data-connection_source-segment': _('Specify source segment')}))

    ip_source = forms.CharField(max_length="255",
                          label=_("Use ip address as source"),
                          required=True,
                          initial="0.0.0.0",
                          widget=forms.TextInput(
                              attrs={'class': 'switched',
                                     'data-connection_source_type-ip': _('Specify source IP address')}))

    tenant_destination = forms.CharField(max_length="255",
                          label=_("Sepecify destination tenant"),
                          required=True,
                          initial="",
                          widget=forms.TextInput(
                              attrs={'class': 'switched',
                                     'data-connection_destination-tenant': _('Specify destination tenant')}))

    segment_destination = forms.CharField(max_length="255",
                          label=_("Sepecify destination segment"),
                          required=True,
                          initial="",
                          widget=forms.TextInput(
                              attrs={'class': 'switched',
                                     'data-connection_destination-segment': _('Specify destination segment')}))

    ip_destination = forms.CharField(max_length="255",
                          label=_("Use ip address as destination"),
                          required=True,
                          initial="0.0.0.0",
                          widget=forms.TextInput(
                              attrs={'class': 'switched',
                                     'data-connection_destination_type-ip': _('Specify destination IP address')}))

    expected_connection = forms.ChoiceField(
        label=_('Expected Connection Results'),
        required=True,
        choices=EXPECTATION_CHOICES,
        widget=forms.Select(attrs={
                'class': 'switchable',
                'data-slug': 'expected_connection'}))

    def __init__(self, *args, **kwargs):
        super(RunQuickTestForm, self).__init__(*args, **kwargs)

    def clean(self):
        cleaned_data = super(RunQuickTestForm, self).clean()

        def update_cleaned_data(key, value):
            cleaned_data[key] = value
            self.errors.pop(key, None)
	
	expected_connection = cleaned_data.get('expected_connection')	
	
	if expected_connection == 'default':
		msg = _('A expected connection result must be selected.')
                raise ValidationError(msg)

	return cleaned_data


    def handle(self, request, data):
        source = {}
        source['tenant'] = data['tenant_source'].encode('ascii')
        source['segment'] = data['segment_source'].encode('ascii')
        source['ip'] = data['ip_source'].encode('ascii','ignore')
        dest = {}
        dest['tenant'] = data['tenant_destination'].encode('ascii')
        dest['segment'] = data['segment_destination'].encode('ascii')
        dest['ip'] = data['ip_destination'].encode('ascii','ignore')
	expected = data['expected_connection'].encode('ascii','ignore')
        new_test_data = {'name' : None,
                        'connection_source' : source,
                        'connection_destination' : dest,
                        'expected_connection' : expected}

        test = ReachabilityQuickTest(tenant_id = tenant_id,\
                                     src_tenant_id = source['tenant'],\
                                     src_segment_id = source['segment'],\
                                     src_ip = source['ip'],\
                                     dst_tenant_id = dest['tenant'],\
                                     dst_segment_id = dest['segment'],\
                                     dst_ip = dest['ip'],\
                                     expected_result = expected)
        api = ReachabilityTestAPI()
        session = Session()
        try:
            api.addQuickTest(test, session)
            api.runQuickTest(tenant_id, session)
            test = api.getQuickTest(tenant_id, session)
            session.commit()
        except:
            session.rollback()
            raise
        finally:
            session.close()

        messages.success(request, _('Successfully ran quick test.'))
        return test


class UpdateForm(forms.SelfHandlingForm):
    reachability_test_id = forms.CharField(widget=forms.HiddenInput())

    name = forms.CharField(max_length="255",
                           label=_("Name"),
                           required=True)

    tenant_source = forms.CharField(max_length="255",
                          label=_("Sepecify source tenant"),
                          required=True,
                          initial="",
                          widget=forms.TextInput(
                              attrs={'class': 'switched',
                                     'data-connection_source-tenant': _('Specify source tenant')}))

    segment_source = forms.CharField(max_length="255",
                          label=_("Sepecify source segment"),
                          required=True,
                          initial="",
                          widget=forms.TextInput(
                              attrs={'class': 'switched',
                                     'data-connection_source-segment': _('Specify source segment')}))

    ip_source = forms.CharField(max_length="255",
                          label=_("Use ip address as source"),
                          required=True,
                          initial="0.0.0.0",
                          widget=forms.TextInput(
                              attrs={'class': 'switched',
                                     'data-connection_source_type-ip': _('Specify source IP address')}))

    tenant_destination = forms.CharField(max_length="255",
                          label=_("Sepecify destination tenant"),
                          required=True,
                          initial="",
                          widget=forms.TextInput(
                              attrs={'class': 'switched',
                                     'data-connection_destination-tenant': _('Specify destination tenant')}))

    segment_destination = forms.CharField(max_length="255",
                          label=_("Sepecify destination segment"),
                          required=True,
                          initial="",
                          widget=forms.TextInput(
                              attrs={'class': 'switched',
                                     'data-connection_destination-segment': _('Specify destination segment')}))

    ip_destination = forms.CharField(max_length="255",
                          label=_("Use ip address as destination"),
                          required=True,
                          initial="0.0.0.0",
                          widget=forms.TextInput(
                              attrs={'class': 'switched',
                                     'data-connection_destination_type-ip': _('Specify destination IP address')}))

    expected_connection = forms.ChoiceField(
        label=_('Expected Connection Results'),
        required=True,
        choices=EXPECTATION_CHOICES,
        widget=forms.Select(attrs={
                'class': 'switchable',
                'data-slug': 'expected_connection'}))

    def __init__(self, *args, **kwargs):
        super(UpdateForm, self).__init__(*args, **kwargs)

    def clean(self):
        cleaned_data = super(UpdateForm, self).clean()

        def update_cleaned_data(key, value):
            cleaned_data[key] = value
            self.errors.pop(key, None)
	
	expected_connection = cleaned_data.get('expected_connection')	
	if expected_connection == 'default':
		msg = _('A expected connection result must be selected.')
                raise ValidationError(msg)

	return cleaned_data

    def handle(self, request, data):
        test_id = data['name'].encode('ascii','ignore')
        source = {}
        source['tenant'] = data['tenant_source'].encode('ascii')
        source['segment'] = data['segment_source'].encode('ascii')
        source['ip'] = data['ip_source'].encode('ascii','ignore')
        dest = {}
        dest['tenant'] = data['tenant_destination'].encode('ascii')
        dest['segment'] = data['segment_destination'].encode('ascii')
        dest['ip'] = data['ip_destination'].encode('ascii','ignore')
	expected = data['expected_connection'].encode('ascii','ignore')
	new_test_data = {'name' : test_id,
                        'connection_source' : source,
                        'connection_destination' : dest,
                        'expected_connection' : expected}

        test = ReachabilityTest(tenant_id = tenant_id,\
                                test_id = test_id,\
                                src_tenant_id = source['tenant'],\
                                src_segment_id = source['segment'],\
                                src_ip = source['ip'],\
                                dst_tenant_id = dest['tenant'],\
                                dst_segment_id = dest['segment'],\
                                dst_ip = dest['ip'],\
                                expected_result = expected)
        api = ReachabilityTestAPI()
        session = Session()
        test = None
        try:
            test = api.updateReachabilityTest(tenant_id, test_id, test, session)
            session.commit()
        except:
            session.rollback()
            raise
        finally:
            session.close()

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
        test_id = data['name'].encode('ascii','ignore')
        api = ReachabilityTestAPI()
        session = Session()
        test = None
        try:
            test = api.saveQuickTest(tenant_id, test_id, session)
            api.saveQuickTestResult(tenant_id, test_id, session)
            session.commit()
        except:
            session.rollback()
            raise
        finally:
            session.close()

        messages.success(request, _('Successfully saved quick test: %s') % data['name'])
	return test
