import time
import datetime
import random

class ReachabilityTestStub():
    """Class to mimick the data added to the reachability test"""
    name = ''
    connection_source = ''
    connection_destination = ''
    expected_connection = ''
    command_line = ''
    last_run = ''
    status = ''
    count = ''
    run_list = []

    def __init__(self,data):
        self.name = data['name']
        self.last_run = "-"
        self.status = "-"
	self.connection_source = data['connection_source']
	self.connection_destination = data['connection_destination']
	self.expected_connection = data['expected_connection']
	self.command_line = "-"
	self.count = 0
	self.run_list = []

    def runTest(self):
	if self.count == 0:
		#self.last_run = "-"
		self.status = "pending"
		self.count += 1
		self.command_line = ""
	else:
		states = ("pass","fail")
		ts = time.time()
		st = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d T %H:%M:%S UTC')
		self.last_run = st
		self.status = random.choice(states)
		self.command_line = self.getCommandLine() 
		self.count = 0

    def getCommandLine(self):
	command_line = "localhost(config-tenant-bvs-acl)# test packet-in src-host 00:00:00:00:00:01 dst-host 00:00:00:00:00:02 src-ip-address 10.0.0.1 dst-ip-address 10.0.0.2 protocol 6 dst-port 80\n<<snipped>>\nSource switch/port : 00:00:00:00:00:00:00:0b/1\nL4 source port : 0\nL4 destination port: 8080\nForward logical path:\n=============\n--------------------------------------\nsrc BVS iface : red-www-if1/00:00:00:00:00:01\ndst BVS iface : red-www-if2/00:00:00:00:00:02\naction : FORWARD\nnext hop IP : 10.0.0.2\nInput ACL:\nInput ACL Name : None\nInput ACL Entry : None\nInput ACL Action : ACL_PERMIT\nOutput ACL:\nOutput ACL Name : red-www|deny-all-except-80\nOutput ACL Entry : 10 permit tcp any any any eq 80\nOutput ACL Action : ACL_PERMIT\nRouting Action : FORWARD\nPhysical Path:\n# Cluster Hop Switch                  Input-Intf   Output-Intf\n-|-------|---|-----------------------|------------|------------\n1 10      1   00:00:00:00:00:00:00:0b 1 (s11-eth1)  3 (s11-eth3)\n2 10      2   00:00:00:00:00:00:00:0a 9 (s10-eth9)  2 (s10-eth2)\n3 10      3   00:00:00:00:00:00:00:0c 2 (s13-eth2)  1 (s13-eth1)"
	return command_line


class NetworkTemplateStub():
    """Class to mimick the data added to the reachability test"""
    network_entities = {}
    network_connections = {}

    def __init__(self,data):
        self.network_entities = data['network_entities']
        self.network_connections  = data['network_connections']

