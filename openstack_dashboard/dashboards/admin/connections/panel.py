from django.utils.translation import ugettext_lazy as _

import horizon

from openstack_dashboard.dashboards.admin import dashboard


class Connections(horizon.Panel):
    name = _("Network Fabric")
    slug = 'connections'


dashboard.Admin.register(Connections)
