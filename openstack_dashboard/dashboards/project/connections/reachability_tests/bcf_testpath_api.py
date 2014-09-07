import eventlet
import json
import rest_lib
import urllib
import logging as log
from openstack_dashboard.dashboards.project.connections import bsn_api


eventlet.monkey_patch()
URL_TEST_PATH = ('applications/bcf/test/path/controller-view'
                 '[src-tenant=\"%(src-tenant)s\"]'
                 '[src-segment=\"%(src-segment)s\"][src-ip=\"%(src-ip)s\"]'
                 '[dst-tenant=\"%(dst-tenant)s\"]'
                 '[dst-segment=\"%(dst-segment)s\"][dst-ip=\"%(dst-ip)s\"]')

class ControllerCluster(object):
    """
    Controller interfaces for a big switch controller cluster
    """
    def __init__(self, controllers=bsn_api.controllers, port=bsn_api.port):
        self.controllers = tuple(controllers)
        self.port = port
        self.cookie = None
        self.origin = 'neutron'

    @property
    def active_controller(self):
        # return first-responder
        pool = eventlet.greenpool.GreenPool()
        coroutines = {}
        for controller in self.controllers:
            coroutines[controller] = pool.spawn(
                rest_lib.request, "", host="%s:%d" % (controller, self.port))
        while True:
            for controller in coroutines:
                if coroutines[controller].dead:
                    return controller
            eventlet.sleep(0.1)
        # neither responded in time, return first in list
        return self.controllers[0]

    def auth(self, username=bsn_api.username, password=bsn_api.password):
        login = {"user": username, "password": password}
        host = "%s:%d" % (self.active_controller, self.port)
        log.info("PRE AUTH: Host: %s\t user: %s password: %s"
                 % (self.active_controller, username, password))
        ret = rest_lib.request("/api/v1/auth/login", prefix='',
                               method='POST', data=json.dumps(login),
                               host=host)
        session = json.loads(ret[2])
        if ret[0] != 200:
            raise Exception(session["error_message"])
        if ("session_cookie" not in session):
            raise Exception("Failed to authenticate: session cookie not set")

        self.cookie = session["session_cookie"]
        return self.cookie

    def logout(self):
        url = "core/aaa/session[auth-token=\"%s\"]" % self.cookie
        ret = rest_lib.delete(self.cookie, url, self.active_controller,
                              self.port)
        log.info("LOGOUT Session: cookie: %s" % self.cookie)
        return ret

    def getTestPath(self, src, dst):
        url = (URL_TEST_PATH %
              {'src-tenant': src['tenant'],
               'src-segment': src['segment'],
               'src-ip': src['ip'],
               'dst-tenant': dst['tenant'],
               'dst-segment': dst['segment'], 'dst-ip': dst['ip']})
        ret = rest_lib.get(self.cookie, url,
                           self.active_controller, self.port)
        data = list()
        if ret[0] in range(200, 300):
            data = json.loads(ret[2])
        return data
