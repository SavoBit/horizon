import os
import json
from sqlalchemy import func, desc
from openstack_dashboard.dashboards.project.connections.reachability_tests.bcf_testpath_api import ControllerCluster
import openstack_dashboard.dashboards.project.connections.reachability_tests.reachability_test_db as db

result_limit = 1

class ReachabilityTestAPI(object):

    def saveTest(self, tenant_id, test_id, test, session):
        session.query(db.ReachabilityTestResult)\
               .filter(db.ReachabilityTestResult.tenant_id == tenant_id,
                       db.ReachabilityTestResult.test_id == test_id)\
               .delete()
        session.query(db.ReachabilityTest)\
               .filter(db.ReachabilityTest.tenant_id == tenant_id,
                       db.ReachabilityTest.test_id == test_id)\
               .delete()
        session.add(test)

    def addReachabilityTest(self, test, session):
        self.saveTest(test.tenant_id, test.test_id, test, session)
        return session.query(db.ReachabilityTest)\
                      .filter(db.ReachabilityTest.tenant_id == test.tenant_id,
                              db.ReachabilityTest.test_id == test.test_id)\
                      .first()

    def addQuickTest(self, test, session):
        session.query(db.ReachabilityQuickTestResult)\
               .filter(db.ReachabilityQuickTestResult.tenant_id == test.tenant_id)\
               .delete()
        session.query(db.ReachabilityQuickTest)\
               .filter(db.ReachabilityQuickTest.tenant_id == test.tenant_id)\
               .delete()
        session.add(test)

    def listReachabilityTests(self, tenant_id, session):
        return session.query(db.ReachabilityTest)\
                      .filter(db.ReachabilityTest.tenant_id == tenant_id)

    def listReachabilityTestResults(self, tenant_id, test_id, session):
        return session.query(db.ReachabilityTestResult)\
                      .filter(db.ReachabilityTestResult.tenant_id == tenant_id,
                              db.ReachabilityTestResult.test_id == test_id)

    def saveQuickTest(self, tenant_id, test_id, session):
        quick_test = session.query(db.ReachabilityQuickTest)\
                            .filter(db.ReachabilityQuickTest.tenant_id == tenant_id)\
                            .first()
        if not quick_test:
            return None
        test = db.ReachabilityTest(tenant_id = tenant_id,
                                   test_id = test_id,
                                   src_tenant_id = quick_test.src_tenant_id,
                                   src_segment_id = quick_test.src_segment_id,
                                   src_ip = quick_test.src_ip,
                                   dst_tenant_id = quick_test.dst_tenant_id,
                                   dst_segment_id = quick_test.dst_segment_id,
                                   dst_ip = quick_test.dst_ip,
                                   expected_result = quick_test.expected_result)
        self.saveTest(tenant_id, test_id, test, session)
        return test

    def saveQuickTestResult(self, tenant_id, test_id, session):
        test = session.query(db.ReachabilityTest)\
                      .filter(db.ReachabilityTest.tenant_id == tenant_id,
                              db.ReachabilityTest.test_id == test_id)\
                      .first()
        if not test:
            return
        quick_results = session.query(db.ReachabilityQuickTestResult)\
                               .filter(db.ReachabilityQuickTestResult.tenant_id == tenant_id)
        for quick_result in quick_results:
            result = db.ReachabilityTestResult(test_primary_key=test.id,
                                               tenant_id = tenant_id,
                                               test_id = test_id,
                                               test_time = quick_result.test_time,
                                               test_result = quick_result.test_result,
                                               detail = quick_result.detail)
            session.add(result)

    def deleteReachabilityTest(self, tenant_id, test_id, session):
        session.query(db.ReachabilityTestResult)\
               .filter(db.ReachabilityTestResult.tenant_id == tenant_id,
                       db.ReachabilityTestResult.test_id == test_id)\
               .delete()
        test = session.query(db.ReachabilityTest)\
                      .filter(db.ReachabilityTest.tenant_id == tenant_id,
                              db.ReachabilityTest.test_id == test_id)\
                      .first()
        if test:
            session.delete(test)

    def deleteQuickTest(self, tenant_id, session):
        session.query(db.ReachabilityQuickTestResult)\
               .filter(db.ReachabilityQuickTestResult.tenant_id == tenant_id)\
               .delete()
        test = session.query(db.ReachabilityQuickTest)\
                      .filter(db.ReachabilityQuickTest.tenant_id == tenant_id)\
                      .delete()

    def getBcfTestResult(self, test):
        src = {}
        src['tenant'] = test.src_tenant_id
        src['segment'] = test.src_segment_id
        src['ip'] = test.src_ip
        dst = {}
        dst['tenant'] = test.dst_tenant_id
        dst['segment'] = test.dst_segment_id
        dst['ip'] = test.dst_ip
        bcf = ControllerCluster()
        bcf.auth()
        data = bcf.getTestPath(src, dst)
        return data

    def runQuickTest(self, tenant_id, session):
        test = session.query(db.ReachabilityQuickTest)\
                      .filter(db.ReachabilityQuickTest.tenant_id == tenant_id)\
                      .first()
        if not test:
            return
        data = self.getBcfTestResult(test)
        test_result = "pending"
        if data and data[0].get("summary", [{}])[0].get("forward-result") == test.expected_result:
            test_result = "pass"
        else:
            test_result = "fail"
        detail = None
        detail = data[0].get("physical-path")
        result = db.ReachabilityQuickTestResult(test_primary_key = test.id,
                                                tenant_id = tenant_id,
                                                test_time = func.now(),
                                                test_result = test_result,
                                                detail = detail)
        session.add(result)
        results = session.query(db.ReachabilityQuickTestResult)\
                         .filter(db.ReachabilityQuickTestResult.tenant_id == tenant_id)\
                         .order_by(db.ReachabilityQuickTestResult.test_time)\
                         .all()
        if(len(results) > result_limit):
            expired_result = results.pop(0)
            session.delete(expired_result)

    def runReachabilityTest(self, tenant_id, test_id, session):
        test = session.query(db.ReachabilityTest)\
                      .filter(db.ReachabilityTest.tenant_id == tenant_id,
                              db.ReachabilityTest.test_id == test_id)\
                      .first()
        if not test:
            return
        data = self.getBcfTestResult(test)
        test_result = "pending"
        if data and data[0].get("summary", [{}])[0].get("forward-result") == test.expected_result:
            test_result = "pass"
        else:
            test_result = "fail"
        detail = data[0].get("physical-path")
        result = db.ReachabilityTestResult(test_primary_key=test.id,
                                           tenant_id = tenant_id,
                                           test_id = test_id,
                                           test_result = test_result,
                                           detail = detail)
        session.add(result)
        results = session.query(db.ReachabilityTestResult)\
                         .filter(db.ReachabilityTestResult.tenant_id == tenant_id,
                                 db.ReachabilityTestResult.test_id == test_id)\
                         .order_by(db.ReachabilityTestResult.test_time)\
                         .all()
        if(len(results) > result_limit):
            expired_result = results.pop(0)
            session.delete(expired_result)

    def getReachabilityTest(self, tenant_id, test_id, session):
        return session.query(db.ReachabilityTest)\
                      .filter(db.ReachabilityTest.tenant_id == tenant_id,
                              db.ReachabilityTest.test_id == test_id)\
                      .first()

    def getLastReachabilityTestResult(self, tenant_id, test_id, session):
        return session.query(db.ReachabilityTestResult)\
                      .filter(db.ReachabilityTestResult.tenant_id == tenant_id,
                              db.ReachabilityTestResult.test_id == test_id)\
                      .order_by(desc(db.ReachabilityTestResult.test_time))\
                      .first()       

    def getQuickTest(self, tenant_id, session):
        return session.query(db.ReachabilityQuickTest)\
                      .filter(db.ReachabilityQuickTest.tenant_id == tenant_id)\
                      .first()

    def getLastReachabilityQuickTestResult(self, tenant_id, session):
        return session.query(db.ReachabilityQuickTestResult)\
                      .filter(db.ReachabilityQuickTestResult.tenant_id == tenant_id)\
                      .order_by(desc(db.ReachabilityQuickTestResult.test_time))\
                      .first()

    def updateReachabilityTest(self, tenant_id, test_id, test, session):
        self.saveTest(tenant_id, test_id, test, session)
        return session.query(db.ReachabilityTest)\
                      .filter(db.ReachabilityTest.tenant_id == tenant_id,
                              db.ReachabilityTest.test_id == test_id)\
                      .first()

