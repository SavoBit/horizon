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

	def deleteReachabilityTest(self,test):
		d = shelve.open(self.dbname)
		del d[test]
		d.close()
