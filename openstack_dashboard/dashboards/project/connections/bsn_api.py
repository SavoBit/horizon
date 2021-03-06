import os

from neutron.db import api
from neutron.db import models_v2
from neutron.db import model_base
from oslo.config import cfg
from oslo.db.sqlalchemy import session
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import openstack_dashboard.dashboards.project.connections.network_template.network_template_db
import openstack_dashboard.dashboards.project.connections.reachability_tests.reachability_test_db


restproxy_opts = [
    cfg.ListOpt('servers', default=['localhost:8800'],
                help=_("A comma separated list of Big Switch or Floodlight "
                       "servers and port numbers. The plugin proxies the "
                       "requests to the Big Switch/Floodlight server, "
                       "which performs the networking configuration. Only one"
                       "server is needed per deployment, but you may wish to"
                       "deploy multiple servers to support failover.")),
    cfg.StrOpt('server_auth', secret=True,
               help=_("The username and password for authenticating against "
                      " the Big Switch or Floodlight controller."))
]
conf = cfg.ConfigOpts()
paths = ['/etc/neutron/neutron.conf', '/etc/neutron/plugin.ini',
         '/usr/share/neutron/neutron-dist.conf',
         '/etc/neutron/plugins/ml2/ml2_conf.ini',
         '/etc/neutron/plugins/bigswitch/restproxy.ini']
params = ["--config-file=%s" % p for p in paths if os.path.exists(p)]
conf.register_opts(restproxy_opts, "RESTPROXY")
conf(params)
api._FACADE = session.EngineFacade.from_config(conf, sqlite_fk=True)

# ignore port from neutron config because it references NSAPI instead of
# floodlight API
controllers = [s.rsplit(':', 1)[0]
               for s in conf.RESTPROXY.servers]
port = 8443
try:
    username, password = conf.RESTPROXY.server_auth.split(':', 1)
except:
    username, password = '', ''
#tenant_id = 'admin'

Session = api.get_session()
Base = model_base.BASEV2()
Base.metadata.create_all(bind=api.get_engine())

