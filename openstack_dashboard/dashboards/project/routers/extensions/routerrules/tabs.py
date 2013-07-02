# vim: tabstop=4 shiftwidth=4 softtabstop=4

# Copyright 2013,  Big Switch Networks, Inc.
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

from django import template
from django.core.urlresolvers import reverse
from django.template.loader import render_to_string
from django.utils.translation import ugettext_lazy as _

from horizon import exceptions
from horizon import tabs
from .tables import RouterRulesTable
from openstack_dashboard import api



class RuleObject(dict):
    pass

class RouterRulesTab(tabs.TableTab):
    table_classes = (RouterRulesTable,)
    name = _("Router Rules")
    slug = "routerrules"
    template_name = "horizon/common/_detail_table.html"

    def get_routerrules_data(self):
        device_id = self.tab_group.kwargs['router_id']
        try:
            routerrules = getattr(self.tab_group.router,'router_rules')
            self._allowed = True
        except:
            routerrules = []
            self._allowed = False
        objectrules = []
        for r in routerrules:
            ro = RuleObject(r)
            ro.id = r['id']
            objectrules.append(ro)
        return objectrules

class RulesGridTab(tabs.Tab):
    name = _("Router Rules Grid")
    slug = "rulesgrid"
    template_name = ("project/routers/routerrules/grid.html")

    def render(self):
        context = template.RequestContext(self.request)
        return render_to_string(self.get_template_name(self.request), self.data, context_instance=context)

    def get_context_data(self, request, **kwargs):
        data = {'router': 
                {'id': 
                 self.tab_group.kwargs['router_id']}
               }
        self.request = request
        rules, supported = self.get_routerrules_data(checksupport=True)
        self._allowed = supported
        data['rulessupported'] = supported
        if supported:
            data["rulesmatrix"] = self.get_routerrulesgrid_data(rules)
        return data
    

    def get_routerrulesgrid_data(self, rules):
        tenant_id = self.request.user.tenant_id
        ports = self.tab_group.ports
        networks = api.quantum.network_list_for_tenant(self.request,
                                                       self.request.user.tenant_id)
        for n in networks:
            n.set_id_as_name_if_empty()
        netnamemap = {}
        subnetmap = {}
        for n in networks:
            netnamemap[n['id']]=n['name']
            for s in n.subnets:
               subnetmap[s.id]={'name':s.name,
                                'cidr':s.cidr}

        matrix = []
        subnets = []
        for port in ports:
            for ip in port['fixed_ips']:
                if ip['subnet_id'] not in subnetmap:
                    continue
                sub = {'ip': ip['ip_address'],
                       'subnetid': ip['subnet_id'],
                       'subnetname': subnetmap[ip['subnet_id']]['name'],
                       'networkid': port['network_id'],
                       'networkname': netnamemap[port['network_id']],
                       'cidr': subnetmap[ip['subnet_id']]['cidr'],
                      }
                subnets.append(sub)
        subnets.append({'ip':'0.0.0.0',
                        'subnetid':'any',
                        'subnetname':'',
                        'networkname': 'external',
                        'networkid':'any',
                        'cidr':'0.0.0.0/0'})
        for source in subnets:
            row={'source': dict(source),
                 'targets': []}
            for target in subnets:
               target.update(self._get_cidr_connectivity(
                                       source['cidr'],
                                       target['cidr'], rules))
               row['targets'].append(dict(target))
            matrix.append(row)
        return matrix

    def _get_cidr_connectivity(self, src, dst, rules):
        connectivity = {'reachable': '',
                        'inverse_rule': {},
                        'rule_to_delete': False}
        if str(src) == str(dst):
           connectivity['reachable'] = 'full'
           return connectivity
        matchingrules=[]
            
        for rule in rules:
            rd = rule['destination']
            if rule['destination']=='any':
                rd = '0.0.0.0/0'
            rs = rule['source']
            if rule['source']=='any':
                rs = '0.0.0.0/0'
            rs = netaddr.IPNetwork(rs)
            src = netaddr.IPNetwork(src)
            rd = netaddr.IPNetwork(rd)
            dst = netaddr.IPNetwork(dst)
            # check if cidrs are affected by rule first
            if ( int(dst.network) >= int(rd.broadcast) or
                 int(dst.broadcast) <= int(rd.network) or
                 int(src.network) >= int(rs.broadcast) or
                 int(src.broadcast) <= int(rs.network) ):
                 continue

            if (str(dst) == '0.0.0.0/0' and 
                str(rd) != '0.0.0.0/0'):
                continue
            if (str(src) == '0.0.0.0/0' and 
                str(rs) != '0.0.0.0/0'):
                continue
            
            match = {'bitsinsrc': rs.prefixlen,
                     'bitsindst': rd.prefixlen,
                     'rule': rule}
            matchingrules.append(match)

        if not matchingrules:
            connectivity['reachable']='none'
            connectivity['inverse_rule']={'source': str(src),
                                          'destination': str(dst),
                                          'action': 'permit'}
            return connectivity

        sortedrules = sorted(matchingrules, key=lambda k: (k['bitsinsrc'],k['bitsindst']), reverse=True)
        match = sortedrules[0]
        if ( match['bitsinsrc'] > src.prefixlen or
             match['bitsindst'] > dst.prefixlen ):
                connectivity['reachable'] = 'partial'
                connectivity['conflicting_rule'] = match['rule']
                return connectivity

        if ( match['bitsinsrc'] == src.prefixlen and
             match['bitsindst'] == dst.prefixlen ):
                connectivity['rule_to_delete']=match['rule']

        if match['rule']['action']=='permit':
            connectivity['reachable']='full'
            inverseaction = 'deny'
        else:
            connectivity['reachable']='none'
            inverseaction = 'permit'
        connectivity['inverse_rule']={'source': str(src),
                                      'destination': str(dst),
                                      'action': inverseaction}
        return connectivity


    def get_routerrules_data(self, checksupport=False):
        device_id = self.tab_group.kwargs['router_id']
        try:
            routerrules = getattr(self.tab_group.router,'router_rules')
            supported = True
        except:
            routerrules = []
            supported = False
        
        if checksupport:
            return routerrules, supported
        return routerrules
