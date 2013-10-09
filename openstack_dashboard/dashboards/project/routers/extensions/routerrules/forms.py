# vim: tabstop=4 shiftwidth=4 softtabstop=4

# Copyright 2013,  Big Switch Networks
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

import json
import logging

from django.core.urlresolvers import reverse
from django.utils.translation import ugettext_lazy as _

from horizon import exceptions
from horizon import forms
from horizon import messages
from horizon.utils import fields
import rulemanager

from openstack_dashboard import api

LOG = logging.getLogger(__name__)


class AddRouterRule(forms.SelfHandlingForm):
    source = forms.TypedChoiceField(label=_("Source"),
                                    empty_value=None)
    source_text = fields.IPField(label=_("If typing, enter IP"
                                         " Address/CIDR here"),
                                  mask=True, required=False)
    destination = forms.DynamicTypedChoiceField(label=_("Destination"),
                                                empty_value=None)
    destination_text = fields.IPField(label=_("If typing, enter IP"
                                              " Address/CIDR here"),
                                      mask=True, required=False)
    action = forms.ChoiceField(label=_("Action"), required=True)
    nexthops = forms.CharField(label=_("Optional: Next Hop "
                                       "Addresses (comma delimited)"),
                               widget=forms.TextInput(), required=False)
    router_id = forms.CharField(label=_("Router ID"),
                                  widget=forms.TextInput(
                                    attrs={'readonly': 'readonly'}))
    failure_url = 'horizon:project:routers:detail'

    def __init__(self, request, *args, **kwargs):
        super(AddRouterRule, self).__init__(request, *args, **kwargs)
        self.fields['action'].choices = [('permit', 'Permit'),
                                         ('deny', 'Deny')]
        try:
            networks = api.quantum.network_list_for_tenant(
                request,
                request.user.tenant_id)
            for n in networks:
                n.set_id_as_name_if_empty()
            self.initial['networks'] = networks
        except:
            redirect = reverse(self.failure_url)
            exceptions.handle(self.request,
                              _('Unable to retrieve networks.'),
                              redirect=redirect)
        options = sorted([(net.id, net.name + ' (' +
                           net.subnets[0].cidr + ')') for net in networks])
        options.append(('external', _('external')))
        options.append(('any', _('any')))

        options.insert(0, ('type',
                            _("Type below or select an existing network")))

        self.fields['source'].choices = options
        self.fields['destination'].choices = options

    def handle(self, request, data):
        any_keywords = ['any', 'external']
        try:
            if 'rule_to_delete' in request.POST:
                rulemanager.remove_rules(request,
                    [request.POST['rule_to_delete']],
                    router_id=data['router_id'])
        except:
            exceptions.handle(request, _('Unable to delete router rule.'))
        try:
            if data['source'] != "type":
                if data['source_text']:
                    raise forms.ValidationError('Specify source from '
                                                'drop-down menu or type in '
                                                'text box, not both.')
                if data['source'] not in any_keywords:
                    data['source'] = [n.subnets[0].cidr
                                      for n in self.initial['networks']
                                      if n.id == data['source']][0]
            else:
                if not data['source_text']:
                    raise forms.ValidationError('Source not specified.')
                data['source'] = data['source_text']

            if data['destination'] != "type":
                if data['destination_text']:
                    raise forms.ValidationError('Specify destination from '
                                                'drop-down menu or type in '
                                                'text box, not both.')
                if data['destination'] not in any_keywords:
                    data['destination'] = [n.subnets[0].cidr
                                           for n in self.initial['networks']
                                           if n.id == data['destination']][0]
            else:
                if not data['destination_text']:
                    raise forms.ValidationError('Destination not specified.')
                data['destination'] = data['destination_text']

            if 'nexthops' not in data:
                data['nexthops'] = ''
            if data['source'] == '0.0.0.0/0':
                data['source'] = 'any'
            if data['destination'] == '0.0.0.0/0':
                data['destination'] = 'any'
            rulemanager.add_rule(request,
                                 router_id=data['router_id'],
                                 action=data['action'],
                                 source=data['source'],
                                 destination=data['destination'],
                                 nexthops=data['nexthops'])
            msg = _('Router rule added')
            LOG.debug(msg)
            messages.success(request, msg)
            return True
        except Exception as e:
            message = getattr(e, 'messages', None)
            if not message:
                message = e.message
            msg = _('Failed to add router rule. '
                    'Hint: %s') % json.dumps(message)
            LOG.info(msg)
            messages.error(request, msg)
            redirect = reverse(self.failure_url, args=[data['router_id']])
            exceptions.handle(request, msg, redirect=redirect)
