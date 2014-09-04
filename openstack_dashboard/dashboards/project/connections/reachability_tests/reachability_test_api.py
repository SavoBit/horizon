import os
import json
from sqlalchemy import func, desc
from openstack_dashboard.dashboards.project.connections.reachability_tests.bcf_testpath_api import Controller
from openstack_dashboard.dashboards.project.connections.reachability_tests.reachability_test_db \
      import ReachabilityTest, ReachabilityTestResult, ReachabilityQuickTest, ReachabilityQuickTestResult
from openstack_dashboard.dashboards.project.connections.reachability_tests.const import debug

result_limit = 1

class ReachabilityTestAPI:

    def saveTest(self, tenant_id, test_id, test, session):
        existing_tests = session.query(ReachabilityTest).filter(ReachabilityTest.tenant_id == tenant_id, ReachabilityTest.test_id == test_id).all()
        if existing_tests == None or len(existing_tests) == 0:
            session.add(test)
        else:
            for existing_test in existing_tests:
                existing_results = session.query(ReachabilityTestResult)\
                                          .filter(ReachabilityTestResult.tenant_id == tenant_id,\
                                                  ReachabilityTestResult.test_id == test_id).all()
                for existing_result in existing_results:
                    session.delete(existing_result)
                session.delete(existing_test)
        session.add(test)
        session.flush()

    def addReachabilityTest(self, test, session):
        self.saveTest(test.tenant_id, test.test_id, test, session)
        return session.query(ReachabilityTest).filter(ReachabilityTest.tenant_id == test.tenant_id, ReachabilityTest.test_id == test.test_id).first()

    def addQuickTest(self, test, session):
        existing_test = session.query(ReachabilityQuickTest).filter(ReachabilityQuickTest.tenant_id == test.tenant_id).first()
        existing_results = session.query(ReachabilityQuickTestResult).filter(ReachabilityQuickTestResult.tenant_id == test.tenant_id).all()
        for existing_result in existing_results:
            session.delete(existing_result)
        if existing_test:
            session.delete(existing_test)
        session.add(test)

    def listReachabilityTests(self, tenant_id, session):
        return session.query(ReachabilityTest).filter(ReachabilityTest.tenant_id == tenant_id).all()

    def listReachabilityTestResults(self, tenant_id, test_id, session):
        return session.query(ReachabilityTestResult).filter(ReachabilityTestResult.tenant_id == tenant_id, ReachabilityTestResult.test_id == test_id).all()

    def saveQuickTest(self, tenant_id, test_id, session):
        quick_test = session.query(ReachabilityQuickTest).filter(ReachabilityQuickTest.tenant_id == tenant_id).first()
        test = None
        if quick_test:
            test = ReachabilityTest(tenant_id = tenant_id,\
                                    test_id = test_id,\
                                    src_tenant_id = quick_test.src_tenant_id,\
                                    src_segment_id = quick_test.src_segment_id,\
                                    src_ip = quick_test.src_ip,\
                                    dst_tenant_id = quick_test.dst_tenant_id,\
                                    dst_segment_id = quick_test.dst_segment_id,\
                                    dst_ip = quick_test.dst_ip,\
                                    expected_result = quick_test.expected_result)
            self.saveTest(tenant_id, test_id, test, session)
        return test

    def saveQuickTestResult(self, tenant_id, test_id, session):
        test = session.query(ReachabilityTest).filter(ReachabilityTest.tenant_id == tenant_id, ReachabilityTest.test_id == test_id).first()
        quick_results = session.query(ReachabilityQuickTestResult).filter(ReachabilityQuickTestResult.tenant_id == tenant_id).all()
        if test:
            for quick_result in quick_results:
                result = ReachabilityTestResult(test_primary_key=test.id,\
                                                tenant_id = tenant_id,\
                                                test_id = test_id,\
                                                test_time = quick_result.test_time,\
                                                test_result = quick_result.test_result,\
                                                detail = quick_result.detail)
                session.add(result)

    def deleteReachabilityTest(self, tenant_id, test_id, session):
        results = session.query(ReachabilityTestResult).filter(ReachabilityTestResult.tenant_id == tenant_id, ReachabilityTestResult.test_id == test_id).all()
        test = session.query(ReachabilityTest).filter(ReachabilityTest.tenant_id == tenant_id, ReachabilityTest.test_id == test_id).first()
        for result in results:
            session.delete(result)
        if test:
            session.delete(test)

    def deleteQuickTest(self, tenant_id, session):
        test = session.query(ReachabilityQuickTest).filter(ReachabilityQuickTest.tenant_id == tenant_id).first()
        results = session.query(ReachabilityQuickTestResult).filter(ReachabilityQuickTestResult.tenant_id == tenant_id).all()
        for result in results:
            session.delete(result)
        if(test):
            session.delete(test)

    def getBcfTestResult(self, test):
        src = {}
        src['tenant'] = test.src_tenant_id
        src['segment'] = test.src_segment_id
        src['ip'] = test.src_ip
        dst = {}
        dst['tenant'] = test.dst_tenant_id
        dst['segment'] = test.dst_segment_id
        dst['ip'] = test.dst_ip
        bcf = Controller()
        bcf.auth()
        data = bcf.getTestPath(src, dst)
        return data

    def runQuickTest(self, tenant_id, session):
        test = session.query(ReachabilityQuickTest).filter(ReachabilityQuickTest.tenant_id == tenant_id).first()
        if test:
            data = self.getBcfTestResult(test)
            debug(str("summary" in data))
            debug(str(data[0]["summary"][0]["forward-result"]))
            test_result = "pending"
            if data and "summary" in data[0] and test.expected_result == data[0]["summary"][0]["forward-result"]:
                test_result = "pass"
            else:
                test_result = "fail"
            detail = None
            if "physical-path" in data[0]:
                detail = data[0]["physical-path"]
            result = ReachabilityQuickTestResult(test_primary_key = test.id,\
                                                 tenant_id = tenant_id,\
                                                 test_time = func.now(),\
                                                 test_result = test_result,\
                                                 detail = detail)
            session.add(result)
            results = session.query(ReachabilityQuickTestResult).filter(ReachabilityQuickTestResult.tenant_id == tenant_id)\
                                                                .order_by(ReachabilityQuickTestResult.test_time).all()
            if(results.__len__() > result_limit):
                expired_result = results.pop(0)
                session.delete(expired_result)

    def runReachabilityTest(self, tenant_id, test_id, session):
        test = session.query(ReachabilityTest).filter(ReachabilityTest.tenant_id == tenant_id, ReachabilityTest.test_id == test_id).first()
        if test:
            data = self.getBcfTestResult(test)
            test_result = "pending"
            if data and "summary" in data[0] and test.expected_result == data[0]["summary"][0]["forward-result"]:
                test_result = "pass"
            else:
                test_result = "fail"
            detail = None
            if "physical-path" in data[0]:
                detail = data[0]["physical-path"]
            result = ReachabilityTestResult(test_primary_key=test.id,\
                                            tenant_id = tenant_id,\
                                            test_id = test_id,\
                                            test_result = test_result,\
                                            detail = detail)
            session.add(result)
            results = session.query(ReachabilityTestResult).filter(ReachabilityTestResult.tenant_id == tenant_id, ReachabilityTestResult.test_id == test_id)\
                                                       .order_by(ReachabilityTestResult.test_time).all()
            if(results.__len__() > result_limit):
                expired_result = results.pop(0)
                session.delete(expired_result)

    def getReachabilityTest(self, tenant_id, test_id, session):
        return session.query(ReachabilityTest).filter(ReachabilityTest.tenant_id == tenant_id, ReachabilityTest.test_id == test_id).first()

    def getLastReachabilityTestResult(self, tenant_id, test_id, session):
        return session.query(ReachabilityTestResult).filter(ReachabilityTestResult.tenant_id == tenant_id, ReachabilityTestResult.test_id == test_id)\
                                                    .order_by(desc(ReachabilityTestResult.test_time)).first()       

    def getQuickTest(self, tenant_id, session):
        return session.query(ReachabilityQuickTest).filter(ReachabilityQuickTest.tenant_id == tenant_id).first()

    def getLastReachabilityQuickTestResult(self, tenant_id, session):
        return session.query(ReachabilityQuickTestResult).filter(ReachabilityQuickTestResult.tenant_id == tenant_id)\
                                                         .order_by(desc(ReachabilityQuickTestResult.test_time)).first()

    def updateReachabilityTest(self, tenant_id, test_id, test, session):
        self.saveTest(tenant_id, test_id, test, session)
        return session.query(ReachabilityTest).filter(ReachabilityTest.tenant_id == tenant_id, ReachabilityTest.test_id == test_id).first()

