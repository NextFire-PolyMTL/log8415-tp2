import asyncio
import logging
from typing import TYPE_CHECKING

from deploy.config import (
    AWS_KEY_PAIR_NAME,
    AWS_RES_NAME,
    AWS_SECURITY_GROUP_NAME,
    DEV,
    IMAGE_ID,
    M4_L_NB,
)
from deploy.utils import ec2_cli, ec2_res, get_default_vpc, wait_instance

if TYPE_CHECKING:
    from mypy_boto3_ec2.service_resource import Instance, KeyPair, SecurityGroup, Vpc

logger = logging.getLogger(__name__)

NB_INSTANCES = M4_L_NB if not DEV else 2


async def setup_infra():
    vpc = get_default_vpc()
    kp = _setup_key_pair()
    sg = _setup_security_group(vpc)
    instances_m4 = _launch_instances(sg, kp)
    tasks = (asyncio.to_thread(wait_instance, inst) for inst in instances_m4)
    await asyncio.gather(*tasks)
    return instances_m4


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
            {
                "FromPort": 8000,
                "ToPort": 8001,
                "IpProtocol": "tcp",
                "IpRanges": [{"CidrIp": vpc.cidr_block}],
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

    instances_m4: list[Instance] = []
    for i in range(NB_INSTANCES):
        zone = avail_zones[i % len(avail_zones)]
        instances = ec2_res.create_instances(
            KeyName=kp.key_name,
            SecurityGroupIds=[sg.id],
            InstanceType='m4.large',
            ImageId=IMAGE_ID,
            MaxCount=1,
            MinCount=1,
            BlockDeviceMappings=[
                {
                    'DeviceName': '/dev/sda1',
                    'Ebs': {
                        'DeleteOnTermination': True,
                        'VolumeSize': 15,
                        'VolumeType': 'gp2',
                    }
                }
            ],
            Placement={'AvailabilityZone': zone},
            TagSpecifications=[{
                'ResourceType': 'instance',
                'Tags': [
                    {
                        'Key': 'Name',
                        'Value': AWS_RES_NAME + getInstanceName(i),
                    },
                ]
            }]
        )
        instances_m4 += instances

    return instances_m4


def getInstanceName(i: int):
    return "_orchestrator" if (i == NB_INSTANCES - 1) else f"_worker_{i + 1}"
