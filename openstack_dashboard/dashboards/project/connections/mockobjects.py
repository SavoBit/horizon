import time
import datetime

class ReachabilityTestStub():
    """Class to mimick the data added to the reachability test"""
    name = ''
    last_run = ''
    status = ''

    def __init__(self,name,last_run,status):
        self.name = name
        self.last_run = last_run
        self.status = status

    def runTest(self):
	ts = time.time()
	st = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d T %H:%M:%S UTC')
	self.last_run = st
	self.status = 'Pass'
