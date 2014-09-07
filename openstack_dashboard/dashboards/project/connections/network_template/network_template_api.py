from openstack_dashboard.dashboards.project.connections import bsn_api
from openstack_dashboard.dashboards.project.connections.network_template import network_template_db


def get_network_templates():
    return bsn_api.Session.query(network_template_db.NetworkTemplate).all()


def get_template_by_id(tid):
    return bsn_api.Session.query(
        network_template_db.NetworkTemplate).filter_by(
            id=tid).first()


def delete_template_by_id(tid):
    with bsn_api.Session.begin(subtransactions=True):
        bsn_api.Session.delete(get_template_by_id(tid))


def create_network_template(name, body):
    with bsn_api.Session.begin(subtransactions=True):
        dbobj = network_template_db.NetworkTemplate(
            body=body, template_name=name)
        bsn_api.Session.add(dbobj)


def update_template_by_id(tid, name, body):
    with bsn_api.Session.begin(subtransactions=True):
        get_template_by_id(tid).update({'template_name': name,
                                        'body': body})
