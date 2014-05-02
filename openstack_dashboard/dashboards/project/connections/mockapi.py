import os
import yaml
import shelve

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
        
	"""Adds a reachability object to the running
	   list of test.
	   argument: ReachabilityTestStub object"""
	def addReachabilityTest(self,test):
		d = shelve.open(self.dbname)
		d[test.name] = test
		d.close()

		c = shelve.open(self.runlistdb)
		c[test.name] = []
		c.close()
	
	"""Adds a quick test a.k.a. troubleshoot to a
	   temporary location in memory.
	   agument: ReachabilityTestStub object"""
	def addQuickTest(self,test):
		d = shelve.open(self.dbname)
		d[self.quick_test] = test
		d.close()

		c = shelve.open(self.runlistdb)
                c[self.quick_test] = []
                c.close()
	
	"""Gets a sorted list of reachability test objects.
	   The function clears any previously ran quick test
	   before returning the list.
	   argument: none
	   return: dictionary"""
	def listReachabilityTest(self):
		d = shelve.open(self.dbname)
		if(d.has_key(self.quick_test)):
			del d[self.quick_test]
		testlist = d.keys()
		testlist.sort()
		returnlist = []
		for item in testlist:
			returnlist.append(d[item])
		d.close()

		c = shelve.open(self.runlistdb)
                if(c.has_key(self.quick_test)):
                        del c[self.quick_test]
		c.close()

		return returnlist
	
	"""Gets a list of the previous reachability test runs
	   for a particular test. It takes the name of the
	   test as key to find the object in the shelve object.
	   It returns a dictionary with the previous
	   timestamps for that test.
	   argument: String
	   return: dictionary"""
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

    		if(run_list.__len__() < 1):
        		return None

    		return run_list

	"""Stores a previously created quick test as a
	   rechability test. It takes the test name as
	   argument to use as key to store into the
	   shelve object. It returns the newly added test.
	   argument: String
	   return: ReachabilityTestStub object"""
	def saveQuickTest(self,test_name):
		d = shelve.open(self.dbname)
		saved_test = d[self.quick_test]
		saved_test.name = test_name
		d[test_name] = saved_test
		d.close()

		c = shelve.open(self.runlistdb)
		saved_run_list = c[self.quick_test]
		c[test_name] = saved_run_list
		c.close()

		return saved_test
		
	"""Delete a reachability test stored in the
	   shelve object. It takes the test name as argument.
	   argument: String"""
	def deleteReachabilityTest(self,test):
		d = shelve.open(self.dbname)
		if(d.has_key(test)):
			del d[test]
		d.close()

		c = shelve.open(self.runlistdb)
		if(c.has_key(test)):
			del c[test]
		c.close()

	"""Delete the quick test from the shelve object. It
	   takes no argument since only one quick test is 
	   permitted at a time so no need to find it."""
	def deleteQuickTest(self):
		d = shelve.open(self.dbname)
		del d[self.quick_test]
		d.close()

		c = shelve.open(self.runlistdb)
                if(c.has_key(self.quick_test)):
                        del c[self.quick_test]
                c.close()

	"""Simulates the running of the quick test. It updates
	   the quick test object with a random pass/fail."""
	def runQuickTest(self):
                c = shelve.open(self.runlistdb)
                self.run_list = c[self.quick_test]
                c.close()

                d = shelve.open(self.dbname)
                data = d[self.quick_test]
                data.runTest()
		data.runTest()
                if(data.status == "pass" or data.status == "fail"):
                        self.run_list.append(data)
                        if(self.run_list.__len__() > 5):
                                self.run_list.pop(0)
                d[self.quick_test] = data
                d.close()

                c = shelve.open(self.runlistdb)
                c[self.quick_test] = self.run_list
                c.close()
	
	"""Simulates the running of the reachability test. The 
	   function updates the object with a pending state if ran
	   for the first time and a random pass/fail if ran again.
	   It takes the test name as argument to find the object 
	   in the shelve.
	   argument: String"""
	def runReachabilityTest(self,test):
		c = shelve.open(self.runlistdb)
		self.run_list = c[test]
		c.close()

		d = shelve.open(self.dbname)
		data = d[test]
		data.runTest()
		if(data.status == "pass" or data.status == "fail"):
			self.run_list.append(data)
			if(self.run_list.__len__() > 5):
				self.run_list.pop(0)
		d[test] = data
		d.close()

		c = shelve.open(self.runlistdb)
		c[test] = self.run_list
		c.close()

	"""Returns the rechability test stored in the 
	   shelve. It takes the test name as argument.
	   argument: String
	   return: ReachabilityTestStub object"""
	def getReachabilityTest(self,test):
		d = shelve.open(self.dbname)
		data = d[test]
		d.close()
		return data
	
	"""Returns the quick test stored in the shelve.
	   return: RechabilityTestStub object"""
	def getQuickTest(self):
		d = shelve.open(self.dbname)
		data = d[self.quick_test]
		d.close()
		return data
	
	"""Updates a current reachabiliyt test stored in
	   the shelve. It takes the test name and the 
	   new reachability test object to replace the
	   old one with.
	   arguments: String, ReachabilityTestStub object"""
	def updateReachabilityTest(self, test_id, data):
		d = shelve.open(self.dbname)
		del d[test_id]
		d[data.name] = data
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
	
	"""Reads the sample heat template file and uses the PyYAML
	   parser to store the data in a dictionary within the
	   shelve."""
	def loadHeatTemplate(self):
		f = open(self.heat_template_file_path)
		dataMap = yaml.safe_load(f)
		f.close()

		h = shelve.open(self.heatdb)
		h[self.heat_template] = dataMap
		h.close()

	"""Returns the heat template object stored in the
	   shelve if it exist. Otherwise it returns an empty
	   dictionary.
	   return: dictionary"""
	def getHeatTemplate(self):
		h = shelve.open(self.heatdb)
		if(h.has_key(self.heat_template)):
			template = h[self.heat_template]
		else:
			template = {}
		h.close()

		return template

	"""Deletes the heat template object if it exist in
	   the shelve. Otherwise, it does nothing."""
	def removeHeatTemplate(self):
		h = shelve.open(self.heatdb)
		if(h.has_key(self.heat_template)):
                        del h[self.heat_template]
		h.close()
	
	"""Updates the heat template with a new dictionary
	   pass on as a parameter.
	   argument: dictionary"""
	def updateHeatTemplate(self,updated_template):
		h = shelve.open(self.heatdb)
		h[self.heat_template] = updated_template
		h.close()
