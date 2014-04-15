import shelve
from openstack_dashboard.dashboards.project.connections.mockobjects import ReachabilityTestStub

class ReachabilityTestAPI:
	"""Simple reachability test API"""
	d = []
	dbname = "mockreachability"
	def addReachabilityTest(self,test):
		d = shelve.open(self.dbname)
		d[test.name] = test
		d.close()

	def listReachabilityTest(self):
		d = shelve.open(self.dbname)
		testlist = d.keys()
		testlist.sort()
		returnlist = []
		for item in testlist:
			returnlist.append(d[item])
		d.close()
		return returnlist
	
	def listTestRuns(self,test_name):
		d = shelve.open(self.dbname)
		run_list = []
		count = 0
		test = d[test_name]
		for item in test.run_list:
	        	run_list.append(test.run_list[count].last_run)
        		count += 1
		d.close()
        	#import pdb
        	#pdb.set_trace()
    		if(run_list.__len__() < 1):
        		return None
    		return run_list
	
		
	
	def deleteReachabilityTest(self,test):
		d = shelve.open(self.dbname)
		del d[test]
		d.close()

	def runReachabilityTest(self,test):
		d = shelve.open(self.dbname)
		data = d[test]
		data.runTest()
		#import pdb
		#pdb.set_trace()
		if(data.status == "pass" or data.status == "fail"):
			data.run_list.append(data)
			if(data.run_list.__len__() > 5):
				data.run_list.pop(0)
		d[test] = data
		#import pdb
		#pdb.set_trace()
		d.close()

	def getReachabilityTest(self,test):
		d = shelve.open(self.dbname)
		data = d[test]
		d.close()
		return data

	def updateReachabilityTest(self, test_id, data):
		d = shelve.open(self.dbname)
		del d[test_id]
		d[data.name] = data
		d.close()
