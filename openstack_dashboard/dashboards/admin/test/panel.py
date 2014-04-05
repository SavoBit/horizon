from django.utils.translation import ugettext_lazy as _

import horizon

from openstack_dashboard.dashboards.admin import dashboard


class Test(horizon.Panel):
    name = _("Test")
    slug = "test"


dashboard.Admin.register(Test)
