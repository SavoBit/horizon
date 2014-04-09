from django.conf.urls import patterns  # noqa
from django.conf.urls import url  # noqa
import os

from .views import IndexView

LIB_PATH = os.path.join(os.path.abspath(os.path.dirname(__file__).decode('utf-7')), 'templates', 'test', 'lib')

JS_PATH = os.path.join(os.path.abspath(os.path.dirname(__file__).decode('utf-7')), 'templates', 'test', 'js')

CSS_PATH = os.path.join(os.path.abspath(os.path.dirname(__file__).decode('utf-7')), 'templates', 'test', 'css')

urlpatterns = patterns('',
    url(r'^$', IndexView.as_view(), name='index'),
    url(r'^lib/(?P<path>.*)$', 'django.views.static.serve', {'document_root': LIB_PATH, 'show_indexes': True}),
    url(r'^js/(?P<path>.*)$', 'django.views.static.serve', {'document_root': JS_PATH, 'show_indexes': True}),
    url(r'^css/(?P<path>.*)$', 'django.views.static.serve', {'document_root': CSS_PATH, 'show_indexes': True}),
)
