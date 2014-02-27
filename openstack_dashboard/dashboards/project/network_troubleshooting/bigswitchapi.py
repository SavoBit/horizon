import urllib
import urllib2
import json


class Controller(object):

    def __init__(self, controller_ip):
        self.controller_ip = controller_ip
        self.floodlight_port = 8080
        self.netapp_port = 80

    def test_packetin(self, smac, sip, dmac, dip):
        headers = {'content-type': 'application/json', "accept": "text/json"}
        attach = self.get_attachpoint_for_mac(smac)
        test_params = {"srcSwitchDpid": attach['switchDPID'],
                       "sourceMACAddress": smac,
                       "srcSwitchInPort": attach['port'],
                       "destinationMACAddress": dmac}
        test_url = '/wm/bvs/explain-packet/json'
        uri = 'http://%s:%s/%s' % (self.controller_ip, self.floodlight_port, test_url)
        request = urllib2.Request(uri, json.dumps(test_params), headers=headers)
        #raise Exception(uri+str(json.dumps(test_params))+str(headers))
        response = urllib2.urlopen(request)
        return json.loads(response.read())

    def get_interfaces(self):
        try:
            return self.interfaces
        except AttributeError:
            pass
        url = '/rest/v1/bvs/device-interface'
        uri = 'http://%s:%s/%s' % (self.controller_ip, self.netapp_port, url)
        request = urllib2.Request(uri)
        response = urllib2.urlopen(request)
        self.interfaces = json.loads(response.read())
        return self.interfaces

    def get_attachpoint_for_mac(self, mac):
        interfaces = self.get_interfaces()
        controller_known_macs = []
        for pair in interfaces:
            try:
                controller_known_macs.append(pair['device']['mac'][0])
                if pair['device']['mac'][0] == mac:
                    return pair['device']['attachmentPoint'][0]
            except KeyError:
                pass
        raise Exception("MAC address %s not known to controller. "
                        "Verify that the host is running."
                        "Known addresses: %s" %(mac, controller_known_macs))

if __name__ == '__main__':
    ctrl = Controller('10.211.1.3')
    print ctrl.test_packetin('fa:16:3e:0c:be:51', '10.0.0.5', 'fa:16:3e:4c:87:cf', '10.0.0.6')
