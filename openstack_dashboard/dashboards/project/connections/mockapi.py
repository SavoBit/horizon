import shelve
from openstack_dashboard.dashboards.project.connections.mockobjects import ReachabilityTestStub

class ReachabilityTestAPI:
	"""Simple reachability test API"""
	d = []
	dbname = "reachabilitydb"
	c = []
	runlistdb = "runlistdb"
	run_list = []	
	quick_test = "temporaryvariabletoholdquicktest"

	def __init__(self):
		self.d = []
		self.dbname = "reachabilitydb"
		self.runlistdb = "runlistdb"
		self.c = []
		self.run_list = []
		self.quick_test = "temporaryvariabletoholdquicktest"

	def addReachabilityTest(self,test):
		d = shelve.open(self.dbname)
		d[test.name] = test
		d.close()
		c = shelve.open(self.runlistdb)
		c[test.name] = []
		c.close()
	
	def addQuickTest(self,test):
		d = shelve.open(self.dbname)
		d[self.quick_test] = test
		d.close()
	

	def listReachabilityTest(self):
		d = shelve.open(self.dbname)
		if(d.has_key(self.quick_test)):
			del d[self.quick_test]
		#import pdb
		#pdb.set_trace()
		testlist = d.keys()
		testlist.sort()
		returnlist = []
		for item in testlist:
			returnlist.append(d[item])
		d.close()
		return returnlist
	
	def listTestRuns(self,test_name):
		c = shelve.open(self.runlistdb)
		if(c.has_key(test_name)):
			self.run_list = c[test_name]
		c.close()
		run_list = []
		count = 0
		for item in self.run_list:
	        	run_list.append(self.run_list[count].last_run)
        		count += 1
        	#import pdb
        	#pdb.set_trace()
    		if(run_list.__len__() < 1):
        		return None
    		return run_list
	
		
	
	def deleteReachabilityTest(self,test):
		d = shelve.open(self.dbname)
		#import pdb
		#pdb.set_trace()
		if(d.has_key(test)):
			del d[test]
		d.close()
		c = shelve.open(self.runlistdb)
		if(c.has_key(test)):
			del c[test]
		c.close()
	
	def deleteQuickTest(self):
		d = shelve.open(self.dbname)
		del d[self.quick_test]
		d.close()
	
	def runReachabilityTest(self,test):
		c = shelve.open(self.runlistdb)
		self.run_list = c[test]
		c.close()
		d = shelve.open(self.dbname)
		data = d[test]
		data.runTest()
		#import pdb
		#pdb.set_trace()
		if(data.status == "pass" or data.status == "fail"):
			#import pdb
			#pdb.set_trace()
			self.run_list.append(data)
			if(self.run_list.__len__() > 5):
				self.run_list.pop(0)

		d[test] = data
		#import pdb
		#pdb.set_trace()
		d.close()
		c = shelve.open(self.runlistdb)
		c[test] = self.run_list
		c.close()

	def getReachabilityTest(self,test):
		d = shelve.open(self.dbname)
		data = d[test]
		d.close()
		return data
	
	def getQuickTest(self):
		d = shelve.open(self.dbname)
		data = d[self.quick_test]
		d.close()
		return data
	
	def updateReachabilityTest(self, test_id, data):
		d = shelve.open(self.dbname)
		del d[test_id]
		d[data.name] = data
		d.close()
		c = shelve.open(self.runlistdb)
		del d[test_id]
		c[data.name] = []
		c.close()
