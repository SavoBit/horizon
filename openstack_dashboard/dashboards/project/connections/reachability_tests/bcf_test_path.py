import json
import rest_lib
import urllib
import logging as log

URL_TEST_PATH = ('applications/bcf/test/path/controller-view'
                 '[src-tenant=\"%(src-tenant)s\"][src-segment=\"%(src-segment)s\"][src-ip=\"%(src-ip)s\"]'
                 '[dst-tenant=\"%(dst-tenant)s\"][dst-segment=\"%(dst-segment)s\"][dst-ip=\"%(dst-ip)s\"]')

class Controller(object):
    """
    Controller interfaces for a big switch controller
    """
    def __init__(self, server='127.0.0.1', port=8080):
        self.server = server
        self.port = port
        self.cookie = None
        self.origin = 'neutron'

    def auth(self, username, password, origin):
        login = {"user": username, "password": password}
        host = "%s:%d" % (self.server, self.port)
        log.info("PRE AUTH: Host: %s\t user: %s password: %s" % (self.server, username, password))
        ret = rest_lib.request("/api/v1/auth/login", prefix='',
                                    method='POST', data=json.dumps(login),
                                    host=host)
        session = json.loads(ret[2])
        if ret[0] != 200:
            raise NotAuthException(session["error_message"])
        if ("session_cookie" not in session):
            raise Exception("Failed to authenticate: session cookie not set")

        self.cookie = session["session_cookie"]
        self.origin = origin
        return self.cookie

    def logout(self):
        url = "core/aaa/session[auth-token=\"%s\"]" % self.cookie
        ret = rest_lib.delete(self.cookie, url, self.server, self.port)
        log.info("LOGOUT Session: cookie: %s" % self.cookie)
        return ret

    def getTestPath(self, src, dst):
        url = (URL_TEST_PATH %
              {'src-tenant': src['tenant'], 'src-segment': src['segment'], 'src-ip': src['ip'],
               'dst-tenant': dst['tenant'], 'dst-segment': dst['segment'], 'dst-ip': dst['ip']})
        ret = rest_lib.get(self.cookie, url, self.server, self.port)
        data = list()
        if ret[0] in range(200, 300):
            data = json.loads(ret[2])
        return data

src = {}
src["tenant"] = "A"
src["segment"] = "A1"
src["ip"] = "10.0.0.1"
dst = {}
dst["tenant"] = "A"
dst["segment"] = "A1"
dst["ip"] = "10.0.0.6"

server = "172.16.54.234"
port = 8080
username = 'admin'
password = 'adminadmin'

bcf = Controller('172.16.54.234', 8080)
bcf.auth(username, password, 'neutron')
data = bcf.getTestPath(src, dst)
print json.dumps(data)
bcf.logout()

