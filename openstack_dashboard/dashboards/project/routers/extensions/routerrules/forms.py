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

import logging

from django.core.urlresolvers import reverse
from django.utils.translation import ugettext_lazy as _

from horizon import forms
from horizon import messages
from horizon import exceptions
import rulemanager

LOG = logging.getLogger(__name__)


class AddRouterRule(forms.SelfHandlingForm):
    source = forms.CharField(label=_("Source"),
                                  widget=forms.TextInput(), required=True)
    destination = forms.CharField(label=_("Destination"),
                                  widget=forms.TextInput(), required=True)
    action = forms.ChoiceField(label=_("Action"), required=True)
    #Uncomment to enable next hop additions
    #nexthops = forms.CharField(label=_("Optional: Next Hop Addresses (comma delimited)"),
    #                              widget=forms.TextInput(), required=False)
    router_id = forms.CharField(label=_("Router ID"),
                                  widget=forms.TextInput(
                                    attrs={'readonly': 'readonly'}))
    failure_url = 'horizon:project:routers:detail'

    def __init__(self, request, *args, **kwargs):
        super(AddRouterRule, self).__init__(request, *args, **kwargs)
        self.fields['action'].choices = [('permit','Permit'),('deny','Deny')]


    def handle(self, request, data):
        try:
            if 'rule_to_delete' in request.POST:
                rulemanager.remove_rules(request, 
                    [request.POST['rule_to_delete']],router_id=data['router_id'])
        except:
            exceptions.handle(request, _('Unable to delete router rule.'))
        try:
            if not 'nexthops' in data:
                data['nexthops']=''
            if data['source'] == '0.0.0.0/0': data['source'] = 'any' 
            if data['destination'] == '0.0.0.0/0': data['destination'] = 'any' 
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
            msg = _('Failed to add router rule %s') % e.message
            LOG.info(msg)
            messages.error(request, msg)
            redirect = reverse(self.failure_url, args=[data['router_id']])
            exceptions.handle(request, msg, redirect=redirect)


