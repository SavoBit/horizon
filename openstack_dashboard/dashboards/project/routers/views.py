# vim: tabstop=4 shiftwidth=4 softtabstop=4

# Copyright 2012,  Nachi Ueno,  NTT MCL,  Inc.
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

"""
Views for managing Quantum Routers.
"""

import logging
from django import shortcuts
from django.core.urlresolvers import reverse_lazy
from django.utils.translation import ugettext_lazy as _
from django.utils.datastructures import SortedDict

import netaddr

from horizon import exceptions
from horizon import forms
from horizon import tables
from horizon import tabs
from openstack_dashboard import api
from .ports.tables import PortsTable
from .routerrules.tables import RouterRulesTable
from .forms import CreateForm
from .tables import RoutersTable


LOG = logging.getLogger(__name__)


class IndexView(tables.DataTableView):
    table_class = RoutersTable
    template_name = 'project/routers/index.html'

    def _get_routers(self, search_opts=None):
        try:
            tenant_id = self.request.user.tenant_id
            routers = api.quantum.router_list(self.request,
                                              tenant_id=tenant_id,
                                              search_opts=search_opts)
        except:
            routers = []
            exceptions.handle(self.request,
                              _('Unable to retrieve router list.'))

        ext_net_dict = self._list_external_networks()

        for r in routers:
            r.set_id_as_name_if_empty()
            self._set_external_network(r, ext_net_dict)
        return routers

    def get_data(self):
        routers = self._get_routers()
        return routers

    def _list_external_networks(self):
        try:
            search_opts = {'router:external': True}
            ext_nets = api.quantum.network_list(self.request,
                                                **search_opts)
            for ext_net in ext_nets:
                ext_net.set_id_as_name_if_empty()
            ext_net_dict = SortedDict((n['id'], n.name) for n in ext_nets)
        except Exception as e:
            msg = _('Unable to retrieve a list of external networks "%s".') % e
            exceptions.handle(self.request, msg)
            ext_net_dict = {}
        return ext_net_dict

    def _set_external_network(self, router, ext_net_dict):
        gateway_info = router.external_gateway_info
        if gateway_info:
            ext_net_id = gateway_info['network_id']
            if ext_net_id in ext_net_dict:
                gateway_info['network'] = ext_net_dict[ext_net_id]
            else:
                msg = _('External network "%s" not found.') % (ext_net_id)
                exceptions.handle(self.request, msg)


class DetailView(tables.MultiTableView):
    table_classes = (PortsTable, RouterRulesTable,)
    template_name = 'project/routers/detail.html'
    failure_url = reverse_lazy('horizon:project:routers:index')

    def post(self, request, *args, **kwargs):
        if request.POST['action'] == 'routerrules__resetrules':
            kwargs['reset_rules'] = True
            api.quantum.router_remove_routerrules(request, [], **kwargs)
            return self.get(request, *args, **kwargs)
        obj_ids = request.POST.getlist('object_ids')
        action = request.POST['action']
        m = action.split('__')[0]
        if obj_ids == [] and len(action.split('__'))>2:
            obj_ids.append(action.split('__')[2])
        if m == 'routerrules':
            try:
                api.quantum.router_remove_routerrules(request, obj_ids, **kwargs)
            except:
                exceptions.handle(request,
                                  _('Unable to delete router rule.'))
        return self.get(request, *args, **kwargs)

    def _get_data(self):
        if not hasattr(self, "_router"):
            try:
                router_id = self.kwargs['router_id']
                router = api.quantum.router_get(self.request, router_id)
                router.set_id_as_name_if_empty(length=0)
            except:
                msg = _('Unable to retrieve details for router "%s".') \
                        % (router_id)
                exceptions.handle(self.request, msg, redirect=self.failure_url)

            if router.external_gateway_info:
                ext_net_id = router.external_gateway_info['network_id']
                try:
                    ext_net = api.quantum.network_get(self.request, ext_net_id,
                                                      expand_subnet=False)
                    ext_net.set_id_as_name_if_empty(length=0)
                    router.external_gateway_info['network'] = ext_net.name
                except Exception as e:
                    msg = _('Unable to retrieve an external network "%s".') \
                        % (ext_net_id)
                    exceptions.handle(self.request, msg)
                    router.external_gateway_info['network'] = ext_net_id

            self._router = router
        return self._router

    def get_context_data(self, **kwargs):
        context = super(DetailView, self).get_context_data(**kwargs)
        context["router"] = self._get_data()
        rules, supported = self.get_routerrules_data(checksupport=True)
        context["rulessupported"] = supported
        if supported:
            context["rulesmatrix"] = self.get_routerrulesgrid_data(rules)
        return context

    def get_interfaces_data(self):
        try:
            device_id = self.kwargs['router_id']
            ports = api.quantum.port_list(self.request,
                                          device_id=device_id)
        except:
            ports = []
            msg = _('Port list can not be retrieved.')
            exceptions.handle(self.request, msg)
        for p in ports:
            p.set_id_as_name_if_empty()
        return ports

    def get_routerrulesgrid_data(self, ruleobjects):
        tenant_id = self.request.user.tenant_id
        ports=self.get_interfaces_data()
        rules = [r.__dict__['_apidict'] for r in ruleobjects]
        networks = api.quantum.network_list_for_tenant(self.request,
                                                           tenant_id)
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
        # Uncomment the following to enable the 'any' subnet
        #subnets.append({'ip':'0.0.0.0',
        #                'subnetid':'any',
        #                'subnetname':'',
        #                'networkname': 'any',
        #                'networkid':'any',
        #                'cidr':'0.0.0.0/0'
        #                })
        for source in subnets:
            row={'source': dict(source),
                 'targets': [],
                  }
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
                rd='0.0.0.0/0'
            rs = rule['source']
            if rule['source']=='any':
                rs='0.0.0.0/0'
            rs=netaddr.IPNetwork(rs)
            src=netaddr.IPNetwork(src)
            rd=netaddr.IPNetwork(rd)
            dst=netaddr.IPNetwork(dst)
            # check if cidrs are affected by rule first
            if ( int(dst.network) >= int(rd.broadcast) or 
                 int(dst.broadcast) <= int(rd.network) or
                 int(src.network) >= int(rs.broadcast) or
                 int(src.broadcast) <= int(rs.network) ):
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
        try:
            device_id = self.kwargs['router_id']
            supported, routerrules = api.quantum.routerrule_list(
                                         self.request, device_id=device_id)
        except:
            routerrules = []
            supported = False
            msg = _('Router rule list can not be retrieved.')
            exceptions.handle(self.request, msg)
        if checksupport:
            return routerrules, supported
        return routerrules


class CreateView(forms.ModalFormView):
    form_class = CreateForm
    template_name = 'project/routers/create.html'
    success_url = reverse_lazy("horizon:project:routers:index")




