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

from django.conf.urls import include  # noqa
from django.conf.urls import patterns  # noqa
from django.conf.urls import url  # noqa
import os
from .views import IndexView

from openstack_dashboard.dashboards.project.connections.\
    top_talkers import urls as top_talkers_urls
from openstack_dashboard.dashboards.project.connections.\
    reachability_tests import urls as reachability_tests_urls
from openstack_dashboard.dashboards.project.connections.\
    network_template import urls as network_template_urls
from openstack_dashboard.dashboards.project.connections import views


CSS_PATH = os.path.join(os.path.abspath(os.path.dirname(__file__).decode('utf-7')), 'templates', 'connections', 'css')
JS_PATH = os.path.join(os.path.abspath(os.path.dirname(__file__).decode('utf-7')), 'templates', 'connections', 'js')
LIB_PATH = os.path.join(os.path.abspath(os.path.dirname(__file__).decode('utf-7')), 'templates', 'connections', 'lib')


urlpatterns = patterns('',
    url(r'^$', views.IndexView.as_view(), name='index'),
    url(r'top_talkers/', include(top_talkers_urls, namespace='top_talkers')),
    url(r'reachability_tests/', include(reachability_tests_urls, namespace='reachability_tests')),
    url(r'network_template/', include(network_template_urls, namespace='network_template')),
    url(r'^css/(?P<path>.*)$', 'django.views.static.serve', {'document_root': CSS_PATH, 'show_indexes': True}),
    url(r'^js/(?P<path>.*)$', 'django.views.static.serve', {'document_root': JS_PATH, 'show_indexes': True}),
    url(r'^lib/(?P<path>.*)$', 'django.views.static.serve', {'document_root': LIB_PATH, 'show_indexes': True}),
)
