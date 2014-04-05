# vim: tabstop=4 shiftwidth=4 softtabstop=4

# Copyright 2012 United States Government as represented by the
# Administrator of the National Aeronautics and Space Administration.
# All Rights Reserved.
#
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

from django.conf.urls import patterns  # noqa
from django.conf.urls import url  # noqa

from openstack_dashboard.dashboards.project.connections.\
    network_template import views


urlpatterns = patterns('',
    url(r'^apply_template/$', views.ApplyTemplateView.as_view(), name='apply'),
    url(r'^select_template/$', views.SelectTemplateView.as_view(), name='select'),
    url(r'^temp_page/$', views.TempPageView.as_view(), name='temp'),
    url(r'^remove_template/$', views.RemoveTemplateView.as_view(), name='remove'),
)
