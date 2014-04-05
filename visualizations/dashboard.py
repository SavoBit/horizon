from django.utils.translation import ugettext_lazy as _

import horizon


class Visualizations(horizon.Dashboard):
    name = _("Visualizations")
    slug = "visualizations"
    panels = ()  # Add your panels here.
    default_panel = ''  # Specify the slug of the dashboard's default panel.


horizon.register(Visualizations)
