class ReachabilityTestStub():
    """Class to mimick the data added to the reachability test"""
    name = ''
    last_run = ''
    status = ''

    def __init__(self,name,last_run,status):
        self.name = name
        self.last_run = last_run
        self.status = status
