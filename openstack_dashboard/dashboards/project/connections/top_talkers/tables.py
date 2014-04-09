# vim: tabstop=4 shiftwidth=4 softtabstop=4

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

from django.template.defaultfilters import title  # noqa
from django.utils.translation import ugettext_lazy as _

from horizon import tables


class ReloadTopTalkers(tables.LinkAction):
    name = "reload"
    verbose_name = _("Reload")
    classes = ("btn-search",)
    url = "horizon:project:connections:index"


class TopTalkersFilterAction(tables.FilterAction):

    def filter(self, table, toptalkers, filter_string):
	"""Naive case-insentivite search. """
	q = filter_string.lower()
	return [toptalker for toptalker in toptalkers
		if q in toptalkers.api_name.lower()]

class TopTalkersTable(tables.DataTable):
    api_name = tables.Column('name', verbose_name=_("Host Name"))
    sent_bytes = tables.Column('sent_bytes', verbose_name=_("Sent Bytes/sec"))
    rcvd_bytes = tables.Column('rcvd_bytes', verbose_name=_("Rcvd Bytes/sec"))
    sent_packets = tables.Column('sent_packets', verbose_name=_("Sent Packets/sec"))
    rcvd_packets = tables.Column('rcvd_packets', verbose_name=_("Rcvd Packets/sec"))

    class Meta:
        name = "toptalkers"
        verbose_name = _("Top Talkers")
        multi_select = False
        table_actions = (TopTalkersFilterAction, ReloadTopTalkers,)
