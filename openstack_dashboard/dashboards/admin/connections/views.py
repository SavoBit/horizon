from horizon import forms
from horizon import tabs

from openstack_dashboard.dashboards.project.connections \
    import tabs as project_tabs


class IndexView(tabs.TabbedTableView):
    tab_group_class = project_tabs.ConnectionsTabs
    template_name = 'project/connections/index.html'
