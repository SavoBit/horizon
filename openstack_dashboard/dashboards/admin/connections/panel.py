from django.utils.translation import ugettext_lazy as _

import horizon

from openstack_dashboard.dashboards.admin import dashboard


class Connections(horizon.Panel):
    name = _("Connections")
    slug = 'connections'


dashboard.Admin.register(Connections)
