from django.conf.urls import include # noqa
from django.conf.urls import patterns  # noqa
from django.conf.urls import url  # noqa
import os

from openstack_dashboard.dashboards.project.connections.\
    network_template import admin_urls as network_template_urls
from .views import IndexView
from openstack_dashboard.dashboards.project.connections import urls as purl

LIB_PATH = os.path.join(os.path.abspath(os.path.dirname(purl.__file__)), 'templates', 'connections', 'lib')

JS_PATH = os.path.join(os.path.abspath(os.path.dirname(purl.__file__)), 'templates', 'connections', 'js')

CSS_PATH = os.path.join(os.path.abspath(os.path.dirname(purl.__file__)), 'templates', 'connections', 'css')

urlpatterns = patterns('',
    url(r'^$', IndexView.as_view(), name='index'),
    url(r'network_template_admin/', include(network_template_urls, namespace='network_template_admin')),
    url(r'^lib/(?P<path>.*)$', 'django.views.static.serve', {'document_root': LIB_PATH, 'show_indexes': True}),
    url(r'^js/(?P<path>.*)$', 'django.views.static.serve', {'document_root': JS_PATH, 'show_indexes': True}),
    url(r'^css/(?P<path>.*)$', 'django.views.static.serve', {'document_root': CSS_PATH, 'show_indexes': True}),
)
