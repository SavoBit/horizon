import time
import datetime
import random

class ReachabilityTestStub():
    """Class to mimick the data added to the reachability test"""
    name = ''
    last_run = ''
    status = ''
    count = ''

    def __init__(self,name,last_run,status):
        self.name = name
        self.last_run = "-"
        self.status = "-"
	self.count = 0

    def runTest(self):
	if self.count == 0:
		self.last_run = "-"
		self.status = "pending"
		self.count += 1
	else:
		states = ("pass","fail")
		ts = time.time()
		st = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d T %H:%M:%S UTC')
		self.last_run = st
		self.status = random.choice(states)
		self.count = 0
