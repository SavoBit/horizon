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

from openstack_dashboard.api import quantum as api

LOG = logging.getLogger(__name__)


def routerrule_list(request, **params):
    if 'router_id' in params:
        params['device_id'] = params['router_id']
    router = api.quantumclient(request).show_router(params['device_id'],
                                                    **params).get('router')
    if 'router_rules' not in router:
        return (False, [])
    for r in router['router_rules']:
        r['nexthops'] = ','.join(r['nexthops'])
    return (True, router['router_rules'])


def remove_rules(request, rule_ids, **kwargs):
    LOG.debug("router_remove_routerrule(): param=%s" % (kwargs))
    router_id = kwargs['router_id']
    if 'reset_rules' in kwargs:
        newrules = [{'source': 'any', 'destination': 'any',
                     'action': 'permit'}]
        currentrules = []
    else:
        supported, currentrules = routerrule_list(request, **kwargs)
        if not supported:
            LOG.debug("router rules not supported by router %s" % router_id)
            return
        newrules = []
    for oldrule in currentrules:
        if str(oldrule['id']) not in rule_ids:
            newrule = {'source': oldrule['source'],
                       'destination': oldrule['destination'],
                       'action': oldrule['action']}
            if hasattr(oldrule, 'nexthops') and not oldrule['nexthops'] == '':
                newrule['nexthops'] = oldrule['nexthops']
            newrules.append(newrule)
    body = {'router_rules': newrules}
    api.quantumclient(request).update_router(router_id, {'router': body})


def add_rule(request, router_id, source,
             destination, action, nexthops=''):
    body = {'router_rules': []}
    newrule = {'source': source,
               'destination': destination,
               'action': action}
    if not nexthops == '':
        newrule['nexthops'] = '+'.join(nexthops.split(','))
    body['router_rules'].append(newrule)
    supported, currentrules = routerrule_list(request,
                                              **{'router_id': router_id})
    for r in currentrules:
        existingrule = {'source': r['source'],
                        'destination': r['destination'],
                        'action': r['action']}
        if r['nexthops'] != '':
            existingrule['nexthops'] = '+'.join(r['nexthops'].split(','))
        body['router_rules'].append(existingrule)
    api.quantumclient(request).update_router(router_id, {'router': body})
