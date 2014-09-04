import json
import rest_lib
import urllib
import logging as log
from openstack_dashboard.dashboards.project.connections.reachability_tests.const import controller, port, username, password

URL_TEST_PATH = ('applications/bcf/test/path/controller-view'
                 '[src-tenant=\"%(src-tenant)s\"][src-segment=\"%(src-segment)s\"][src-ip=\"%(src-ip)s\"]'
                 '[dst-tenant=\"%(dst-tenant)s\"][dst-segment=\"%(dst-segment)s\"][dst-ip=\"%(dst-ip)s\"]')

class Controller(object):
    """
    Controller interfaces for a big switch controller
    """
    def __init__(self, controller=controller, port=port):
        self.controller = controller
        self.port = port
        self.cookie = None
        self.origin = 'neutron'

    def auth(self, username=username, password=password):
        login = {"user": username, "password": password}
        host = "%s:%d" % (self.controller, self.port)
        log.info("PRE AUTH: Host: %s\t user: %s password: %s" % (self.controller, username, password))
        ret = rest_lib.request("/api/v1/auth/login", prefix='',
                                    method='POST', data=json.dumps(login),
                                    host=host)
        session = json.loads(ret[2])
        if ret[0] != 200:
            raise NotAuthException(session["error_message"])
        if ("session_cookie" not in session):
            raise Exception("Failed to authenticate: session cookie not set")

        self.cookie = session["session_cookie"]
        return self.cookie

    def logout(self):
        url = "core/aaa/session[auth-token=\"%s\"]" % self.cookie
        ret = rest_lib.delete(self.cookie, url, self.controller, self.port)
        log.info("LOGOUT Session: cookie: %s" % self.cookie)
        return ret

    def getTestPath(self, src, dst):
        url = (URL_TEST_PATH %
              {'src-tenant': src['tenant'], 'src-segment': src['segment'], 'src-ip': src['ip'],
               'dst-tenant': dst['tenant'], 'dst-segment': dst['segment'], 'dst-ip': dst['ip']})
        ret = rest_lib.get(self.cookie, url, self.controller, self.port)
        data = list()
        if ret[0] in range(200, 300):
            data = json.loads(ret[2])
        return data

