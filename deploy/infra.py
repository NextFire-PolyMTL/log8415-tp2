import asyncio
import logging
from itertools import chain
from typing import TYPE_CHECKING

from deploy.config import (
    AWS_KEY_PAIR_NAME,
    AWS_RES_NAME,
    AWS_SECURITY_GROUP_NAME,
    DEV,
    IMAGE_ID,
    M4_L_NB,
    T2_L_NB,
)
from deploy.utils import ec2_cli, ec2_res, elbv2_cli, get_default_vpc, wait_instance

if TYPE_CHECKING:
    from mypy_boto3_ec2.service_resource import Instance, KeyPair, SecurityGroup, Vpc

logger = logging.getLogger(__name__)


async def setup_infra():
    vpc = get_default_vpc()
    kp = _setup_key_pair()
    sg = _setup_security_group(vpc)
    instances_m4, instances_t2 = _launch_instances(sg, kp)
    async with asyncio.TaskGroup() as tg:
        for inst in chain(instances_m4, instances_t2):
            tg.create_task(asyncio.to_thread(wait_instance, inst))
    _setup_load_balancer(sg, vpc, instances_m4, instances_t2)
    return instances_m4, instances_t2


def _setup_key_pair():
    logger.info('Setting up key pair')
    key_pair = ec2_res.create_key_pair(KeyName=AWS_KEY_PAIR_NAME)

    with open(f'{AWS_KEY_PAIR_NAME}.pem', 'w') as f:
        f.write(key_pair.key_material)

    return key_pair


def _setup_security_group(vpc: 'Vpc'):
    logger.info('Setting up security group')
    sg = ec2_res.create_security_group(
        GroupName=AWS_SECURITY_GROUP_NAME,
        Description=AWS_SECURITY_GROUP_NAME,
        VpcId=vpc.id,
    )
    sg.authorize_ingress(
        IpPermissions=[
            {
                "FromPort": 22,
                "ToPort": 22,
                "IpProtocol": "tcp",
                "IpRanges": [{"CidrIp": "0.0.0.0/0"}],
            },
            {
                "FromPort": 80,
                "ToPort": 80,
                "IpProtocol": "tcp",
                "IpRanges": [{"CidrIp": "0.0.0.0/0"}],
            },
        ],
    )
    return sg


def _launch_instances(sg: 'SecurityGroup', kp: 'KeyPair'):
    logger.info('Launching instances')

    avail_zones = [zone['ZoneName']
                   for zone
                   in ec2_cli.describe_availability_zones()['AvailabilityZones']
                   if 'ZoneName' in zone]

    instances_m4 = []
    for i in range(M4_L_NB if not DEV else 1):
        zone = avail_zones[i % len(avail_zones)]
        instances = ec2_res.create_instances(
            KeyName=kp.key_name,
            SecurityGroupIds=[sg.id],
            InstanceType='m4.large',
            ImageId=IMAGE_ID,
            MaxCount=1,
            MinCount=1,
            Placement={'AvailabilityZone': zone},
            TagSpecifications=[{
                'ResourceType': 'instance',
                'Tags': [
                    {'Key': 'Name', 'Value': AWS_RES_NAME},
                ]
            }]
        )
        instances_m4 += instances

    instances_t2 = []
    for i in range(T2_L_NB if not DEV else 1):
        zone = avail_zones[-1 - i % len(avail_zones)]  # reverse order
        instances = ec2_res.create_instances(
            KeyName=kp.key_name,
            SecurityGroupIds=[sg.id],
            InstanceType='t2.large',
            ImageId=IMAGE_ID,
            MaxCount=1,
            MinCount=1,
            Placement={'AvailabilityZone': zone},
            TagSpecifications=[{
                'ResourceType': 'instance',
                'Tags': [
                    {'Key': 'Name', 'Value': AWS_RES_NAME},
                ]
            }]
        )
        instances_t2 += instances

    return instances_m4, instances_t2


def _setup_load_balancer(sg: 'SecurityGroup',
                         vpc: 'Vpc',
                         cluster1_instances: list['Instance'],
                         cluster2_instances: list['Instance']):
    logger.info('Setting up load balancer')
    subnets = [subnet.id for subnet in vpc.subnets.all()]
    lb = elbv2_cli.create_load_balancer(
        Name=AWS_RES_NAME,
        Subnets=subnets,
        SecurityGroups=[sg.id],
    )
    logger.debug(lb)
    lb_arn = lb['LoadBalancers'][0].get('LoadBalancerArn')
    if lb_arn is None:
        raise RuntimeError('Load balancer ARN not found')
    lb_dns = lb['LoadBalancers'][0].get('DNSName')
    if lb_dns is None:
        raise RuntimeError('Load balancer DNS not found')
    logger.info(f'Load balancer DNS: {lb_dns}')

    logger.info('Setting up target groups')
    tg1_arn = _create_target_group(
        f'{AWS_RES_NAME}-1', vpc, cluster1_instances)
    tg2_arn = _create_target_group(
        f'{AWS_RES_NAME}-2', vpc, cluster2_instances)

    logger.info('Setting up listener')
    listener = elbv2_cli.create_listener(
        LoadBalancerArn=lb_arn,
        Protocol='HTTP',
        Port=80,
        DefaultActions=[
            {
                "Type": "fixed-response",
                "FixedResponseConfig": {
                    "StatusCode": "404"
                }
            }
        ],
    )
    listener_arn = listener['Listeners'][0].get('ListenerArn')
    if listener_arn is None:
        raise RuntimeError('Listener ARN not found')
    elbv2_cli.create_rule(
        ListenerArn=listener_arn,
        Conditions=[
            {'Field': 'path-pattern', 'Values': ['/cluster1', '/cluster1/*']},
        ],
        Priority=1,
        Actions=[
            {'Type': 'forward', 'TargetGroupArn': tg1_arn},
        ],
    )
    elbv2_cli.create_rule(
        ListenerArn=listener_arn,
        Conditions=[
            {'Field': 'path-pattern', 'Values': ['/cluster2', '/cluster2/*']},
        ],
        Priority=2,
        Actions=[
            {'Type': 'forward', 'TargetGroupArn': tg2_arn},
        ],
    )

    return lb_arn


def _create_target_group(name: str, vpc: 'Vpc', instances: list['Instance']):
    resp = elbv2_cli.create_target_group(
        Name=name,
        Protocol='HTTP',
        Port=80,
        VpcId=vpc.id,
        HealthCheckPath='/health',
    )
    arn = resp['TargetGroups'][0].get('TargetGroupArn')
    if arn is None:
        raise RuntimeError('Target group ARN not found')
    elbv2_cli.register_targets(TargetGroupArn=arn, Targets=[
        {'Id': inst.id, 'Port': 80} for inst in instances
    ])
    return arn
