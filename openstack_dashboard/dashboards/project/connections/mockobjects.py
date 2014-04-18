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
	else:
		states = ("pass","fail")
		ts = time.time()
		st = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d T %H:%M:%S UTC')
		self.last_run = st
		self.status = random.choice(states)
		self.count = 0
