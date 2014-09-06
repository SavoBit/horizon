from neutron.db import models_v2
from neutron.db import model_base
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import openstack_dashboard.dashboards.project.connections.reachability_tests.reachability_test_db

controller = "172.16.54.234"
port = 8080
username = 'admin'
password = 'adminadmin'

db_ip = '127.0.0.1'
db_user = 'root'
db_pwd = 'password'
tenant_id = 'admin'
engine_string = "mysql+mysqldb://%s:%s@%s/neutron?charset=utf8" % (db_user, db_pwd, db_ip)
engine = create_engine(engine_string)
Session = sessionmaker(bind=engine, expire_on_commit=False, autocommit=True)
Base = model_base.BASEV2()
Base.metadata.create_all(bind=engine)

