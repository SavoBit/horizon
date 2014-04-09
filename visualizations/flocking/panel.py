from django.utils.translation import ugettext_lazy as _

import horizon

from visualizations import dashboard


class Flocking(horizon.Panel):
    name = _("Flocking")
    slug = "flocking"


dashboard.Visualizations.register(Flocking)
