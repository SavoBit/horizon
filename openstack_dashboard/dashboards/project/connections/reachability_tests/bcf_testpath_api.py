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
        pool = eventlet.greenpool.GreenPool()
        coroutines = {}
        active = None
        standby_offline = []
        for controller in self.controllers:
            coroutines[controller] = pool.spawn(self.auth, controller)
        while coroutines:
            completed = None
            for controller in coroutines.keys():
                if coroutines[controller].dead:
                    completed = controller
                    break
            eventlet.sleep(0.1)
            if completed:
                coro = coroutines.pop(completed)
                try:
                    cookie = coro.wait()
                    url = 'core/controller/role'
                    res = rest_lib.get(cookie, url, controller,
                                       self.port)[2]
                    if 'active' in res:
                        active = controller
                        self.cookie = cookie
                    else:
                        standby_offline.append((cookie, controller))
                        self.logout(cookie, controller)
                except:
                    standby_offline.append(('', controller))
            if active:
                pool.spawn(self.cleanup_remaining, standby_offline, coroutines)
                return active
        # none responded in time, return first in list
        return self.controllers[0]

    def cleanup_remaining(self, finished, waiting):
        for cookie, controller in finished:
            if not cookie:
                continue
            self.logout(cookie, controller)
        for controller in waiting.keys():
            try:
                cookie = waiting[controller].wait()
                self.logout(cookie, controller)
            except:
                pass

    def auth(self, server, username=bsn_api.username,
             password=bsn_api.password):
        login = {"user": username, "password": password}
        host = "%s:%d" % (server, self.port)
        log.info("PRE AUTH: Host: %s\t user: %s password: %s"
                 % (server, username, password))
        ret = rest_lib.request("/api/v1/auth/login", prefix='',
                               method='POST', data=json.dumps(login),
                               host=host)
        session = json.loads(ret[2])
        if ret[0] != 200:
            raise Exception(session["error_message"])
        if ("session_cookie" not in session):
            raise Exception("Failed to authenticate: session cookie not set")

        return session["session_cookie"]

    def logout(self, cookie, controller):
        url = "core/aaa/session[auth-token=\"%s\"]" % cookie
        ret = rest_lib.delete(cookie, url, controller, self.port)
        log.info("LOGOUT Session: cookie: %s" % cookie)
        return ret

    def getTestPath(self, src, dst):
        url = (URL_TEST_PATH %
               {'src-tenant': src['tenant'],
                'src-segment': src['segment'],
                'src-ip': src['ip'],
                'dst-tenant': dst['tenant'],
                'dst-segment': dst['segment'], 'dst-ip': dst['ip']})
        controller = self.active_controller
        ret = rest_lib.get(self.cookie, url,
                           controller, self.port)
        data = list()
        if ret[0] in range(200, 300):
            data = json.loads(ret[2])
        return data
