# vim: tabstop=4 shiftwidth=4 softtabstop=4

# Copyright 2012,  Nachi Ueno,  NTT MCL,  Inc.
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
from .ports.tables import PortsTable
from .extensions.routerrules.tabs import RouterRulesTab
from .extensions.routerrules.tabs import RulesGridTab
from openstack_dashboard import api


class InterfacesTab(tabs.TableTab):
    table_classes = (PortsTable,)
    name = _("Interfaces")
    slug = "interfaces"
    template_name = "horizon/common/_detail_table.html"

    def get_interfaces_data(self):
        ports = self.tab_group.ports
        for p in ports:
            p.set_id_as_name_if_empty()
        return ports


class RouterDetailTabs(tabs.TabGroup):
    slug = "router_details"
    tabs = (InterfacesTab, RulesGridTab, RouterRulesTab)
    sticky = True

    def __init__(self, request, **kwargs):
        rid = kwargs['router_id']
        self.router = kwargs['router']
        try:
            self.ports = api.quantum.port_list(request, device_id=rid)
        except:
            self.ports = []
            self.router = {}
            msg = _('Router information can not be retrieved.')
            exceptions.handle(request, msg)
        super(RouterDetailTabs, self).__init__(request, **kwargs)
