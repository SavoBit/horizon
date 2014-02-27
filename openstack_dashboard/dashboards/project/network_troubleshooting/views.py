# vim: tabstop=4 shiftwidth=4 softtabstop=4

# Copyright 2012 United States Government as represented by the
# Administrator of the National Aeronautics and Space Administration.
# All Rights Reserved.
#
# Copyright 2013 NTT MCL Inc.
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

from django.conf import settings
from django.core.urlresolvers import reverse
from django.core.urlresolvers import reverse_lazy
from django.http import HttpResponse  # noqa
from django.views.generic import TemplateView  # noqa
from django.views.generic import View  # noqa
from horizon import forms
from horizon import messages
from horizon.utils import fields
from horizon import tables
from openstack_dashboard import api
from django.utils.translation import ugettext_lazy as _


from openstack_dashboard.dashboards.project.network_troubleshooting import bigswitchapi

def _target_title_gen(target):
    return target.id


class TroubleshootingForm(forms.SelfHandlingForm):
    source = forms.ChoiceField(label=_("Select Source"),
             widget=fields.SelectWidget(attrs={'class': 'source-selector'},
             data_attrs=('ipaddress', 'macaddress', 'instance'),
             transform=_target_title_gen))
    destination = forms.ChoiceField(label=_("Select Destination"),
                  widget=fields.SelectWidget(attrs={'class': 'source-selector'},
                  data_attrs=('ipaddress', 'macaddress', 'instance'),
                  transform=_target_title_gen))

    def __init__(self, request, *args, **kwargs):
        super(TroubleshootingForm, self).__init__(request, *args, **kwargs)
        ports = api.neutron.port_list(request, search_opts={'paginate': False})
        servers, more = api.nova.server_list(self.request, search_opts={'paginate': False})
        #raise Exception(servers)
        choices = []
        for server in servers:
            for network in server.addresses:
                 for add in server.addresses[network]:
                     choices.append(('%s|%s' % (add['OS-EXT-IPS-MAC:mac_addr'], add['addr']),
                                     '%s (%s)' % (server.name, add['addr'])))
        self.fields['source'].choices = choices
        self.fields['source'].choices.insert(0, ("", _("Select Source")))
        self.fields['destination'].choices = choices
        self.fields['destination'].choices.insert(0, ("", _("Select Destination")))

    def handle(self, request, data):
        #return False
        return True

class TroubleshootingView(forms.ModalFormView):
    template_name = 'project/network_troubleshooting/select.html'
    form_class = TroubleshootingForm
    success_url = 'horizon:project:network_troubleshooting:endpointtest'

    def get_success_url(self):
        return reverse(self.success_url,
                       args=(self.request.POST['source'], self.request.POST['destination']))
        return '%s-%s' % (self.request.POST['source'], self.request.POST['destination'])


class TroublshootingTable(tables.DataTable):
    name = tables.Column("name", verbose_name=_('f'))
    limit = tables.Column("limit", verbose_name=_('Limit'))

    def get_object_id(self, obj):
        return 'd'

    class Meta:
        name = "troubleshootingtable"
        verbose_name = _("Troubleshooting Table")



class TroubleshootingTest(tables.DataTableView):
    table_class = TroublshootingTable
    template_name = 'project/network_troubleshooting/index.html'

    def get_context_data(self, **kwargs):
        controller = bigswitchapi.Controller('10.211.1.3')
        smac = kwargs['source_id'].split('|')[0]
        sip = kwargs['source_id'].split('|')[-1]
        dmac = kwargs['dest_id'].split('|')[0]
        dip = kwargs['dest_id'].split('|')[-1]
        stest = controller.test_packetin(dmac, dip, smac, sip)
        stest['source'] = sip
        stest['destination'] = dip
        stest['reason'] = stest['expPktVRouting'][0]['dropReason'].split('<')[0]
        rtest = controller.test_packetin(smac, sip, dmac, dip)
        rtest['source'] = dip
        rtest['destination'] = sip
        rtest['reason'] = rtest['expPktVRouting'][0]['dropReason'].split('<')[0]

        data = {'sendresponse': stest , 'returnresponse': rtest,
                'source': sip, 'destination': dip,
                'sbody': json.dumps(stest),
                'rbody': json.dumps(rtest),
                'tests': [stest, rtest]}
        #raise Exception(data)
        return data


    def get_data(self):
        data = {}
        return data
