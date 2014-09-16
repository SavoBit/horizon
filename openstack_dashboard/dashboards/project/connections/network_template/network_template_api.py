import json
from openstack_dashboard.api import heat
from openstack_dashboard.dashboards.project.connections import bsn_api
from openstack_dashboard.dashboards.project.connections.network_template import network_template_db


def get_network_templates():
    return bsn_api.Session.query(network_template_db.NetworkTemplate).all()


def get_template_by_id(tid):
    return bsn_api.Session.query(
        network_template_db.NetworkTemplate).filter_by(
            id=tid).first()


def get_tenant_stack_assignment(tid):
    return bsn_api.Session.query(
        network_template_db.NetworkTemplateAssignment).filter_by(
            tenant_id=tid).first()


def delete_associated_stack(request):
    assign = get_tenant_stack_assignment(request.user.tenant_id)
    if not assign:
        return
    hc = heat.heatclient(request)
    # we only want the one that matches the network template
    stacks = [s for s in hc.stacks.list(tenant_id=request.user.tenant_id)
              if s.id == assign.stack_id]
    if stacks:
        hc.stacks.delete(assign.stack_id)
    with bsn_api.Session.begin(subtransactions=True):
        bsn_api.Session.delete(assign)


def get_stack_topology(request):
    assign = get_tenant_stack_assignment(request.user.tenant_id)
    if not assign:
        return {"network_entities": "{}",
                "network_connections": "{}"}
    hc = heat.heatclient(request)
    # we only want the one that matches the network template
    stacks = [s for s in hc.stacks.list(tenant_id=request.user.tenant_id)
              if s.id == assign.stack_id]
    if not stacks:
        # leftover association
        delete_associated_stack(request)
        return {"network_entities": "",
                "network_connections": ""}
    resources = hc.resources.list(assign.stack_id)
    entities = {}
    connections = []
    for res in resources:
        if res.resource_type in ('OS::Neutron::Router', 'OS::Neutron::Subnet'):
            entities[res.physical_resource_id] = {
                'properties': {'name': res.physical_resource_id}
            }
        if res.resource_type == 'OS::Neutron::RouterInterface':
            connections.append({
                'source': res.physical_resource_id.split(':subnet_id=')[0],
                'destination': res.physical_resource_id.split('subnet_id=')[-1],
                'expected_connection': 'forward'
            })
    resp = {'network_entities': json.dumps(entities),
            'network_connections': json.dumps(connections),
            'stack_resources': resources,
            'stack': stacks[0]}
    return resp


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


def update_assignment_by_tenant_id(tid, data):
    with bsn_api.Session.begin(subtransactions=True):
        db_obj = get_tenant_stack_assignment(tid)
        db_obj.update(data)


def extract_fields_from_body(request, body):
    hc = heat.heatclient(request)
    res = hc.stacks.validate(template=body)
    return res


def deploy_instance(request, tid , params):
    template = get_template_by_id(tid)
    with bsn_api.Session.begin(subtransactions=True):
        body = template.body
        db_obj = network_template_db.NetworkTemplateAssignment(
            template_id=tid, tenant_id=request.user.tenant_id,
            stack_id="PENDING")
        bsn_api.Session.add(db_obj)
    args = {
        'stack_name': "auto-%s" % template.template_name,
        'parameters': params,
        'template': body
    }
    hc = heat.heatclient(request)
    req = hc.stacks.create(**args)
    update_assignment_by_tenant_id(
        request.user.tenant_id, {'stack_id': req['stack']['id']})
