import os
import yaml
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
		c = shelve.open(self.runlistdb)
                c[self.quick_test] = []
                c.close()
	

	def listReachabilityTest(self):
		d = shelve.open(self.dbname)
		if(d.has_key(self.quick_test)):
			del d[self.quick_test]
		#import pdb
		#pdb.set_trace()
		testlist = d.keys()
		testlist.sort()
		#import pdb
		#pdb.set_trace()
		returnlist = []
		for item in testlist:
			returnlist.append(d[item])
		d.close()
		c = shelve.open(self.runlistdb)
                if(c.has_key(self.quick_test)):
                        del c[self.quick_test]
		c.close()
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

	def saveQuickTest(self,test_name):
		d = shelve.open(self.dbname)
		saved_test = d[self.quick_test]
		saved_test.name = test_name
		d[test_name] = saved_test
		#import pdb
		#pdb.set_trace()
		d.close()
		c = shelve.open(self.runlistdb)
		saved_run_list = c[self.quick_test]
		c[test_name] = saved_run_list
		c.close()

		return saved_test
		
	
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
		c = shelve.open(self.runlistdb)
                if(c.has_key(self.quick_test)):
                        del c[self.quick_test]
                c.close()

	def runQuickTest(self):
                c = shelve.open(self.runlistdb)
                self.run_list = c[self.quick_test]
                c.close()
                d = shelve.open(self.dbname)
                data = d[self.quick_test]
                data.runTest()
		data.runTest()
                #import pdb
                #pdb.set_trace()
                if(data.status == "pass" or data.status == "fail"):
                        #import pdb
                        #pdb.set_trace()
                        self.run_list.append(data)
                        if(self.run_list.__len__() > 5):
                                self.run_list.pop(0)

                d[self.quick_test] = data
                #import pdb
                #pdb.set_trace()
                d.close()
                c = shelve.open(self.runlistdb)
                c[self.quick_test] = self.run_list
                c.close()
	

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
		#import pdb
		#pdb.set_trace()
		del d[test_id]
		d[data.name] = data
		#import pdb
		#pdb.set_trace()
		d.close()
		c = shelve.open(self.runlistdb)
		del c[test_id]
		c[data.name] = []
		c.close()



class NetworkTemplateAPI:
        """Simple Network Template API"""
        heatdb = "heatdb"
        heat_template = "temporaryvariabletoholdexampleheattemplate"
        h = []
	heat_template_file_path = ""

        def __init__(self):
                self.heatdb = "heatdb"
                self.h = []
                self.heat_template = "temporaryvariabletoholdexampleheattemplate"
		self.heat_template_file_path = os.path.abspath(os.path.join(os.path.dirname(__file__),"sample_heat_templates","basic_3tier.yaml"))

	def loadHeatTemplate(self):
		#import pdb
		#pdb.set_trace()
		f = open(self.heat_template_file_path)
		dataMap = yaml.safe_load(f)
		f.close()
		h = shelve.open(self.heatdb)
		h[self.heat_template] = dataMap
		h.close()

	def getHeatTemplate(self):
		h = shelve.open(self.heatdb)
		if(h.has_key(self.heat_template)):
			template = h[self.heat_template]
		else:
			template = []
		h.close()
		return template

	def removeHeatTemplate(self):
		h = shelve.open(self.heatdb)
		if(h.has_key(self.heat_template)):
                        del h[self.heat_template]
		h.close()
