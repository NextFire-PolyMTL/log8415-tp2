import logging

import backoff
from botocore.exceptions import ClientError

from deploy.config import (
    AWS_KEY_PAIR_NAME,
    AWS_RES_NAME,
    AWS_SECURITY_GROUP_NAME,
    LOG_LEVEL,
)
from deploy.utils import ec2_res, elbv2_cli, get_error_code

logger = logging.getLogger(__name__)


def giveup(e: Exception):
    return not (isinstance(e, ClientError) and
                (get_error_code(e) in ('DependencyViolation', 'ResourceInUse')))


def terminate_ec2():
    instances = ec2_res.instances.filter(
        Filters=[
            {'Name': 'tag:Name', 'Values': [AWS_RES_NAME]},
            {'Name': 'instance-state-name', 'Values': ['pending', 'running']},
        ]
    )
    for inst in instances:
        logger.info(f"Terminating instance: {inst}")
        inst.terminate()


def delete_lb():
    lbs = elbv2_cli.describe_load_balancers()
    for lb in lbs['LoadBalancers']:
        name = lb.get('LoadBalancerName')
        if name == AWS_RES_NAME:
            arn = lb.get('LoadBalancerArn')
            if arn is None:
                raise RuntimeError('Load balancer ARN not found')
            logger.info(f"Deleting load balancer: {arn}")
            elbv2_cli.delete_load_balancer(LoadBalancerArn=arn)
            break


@backoff.on_exception(backoff.constant, ClientError, giveup=giveup)
def delete_target_groups():
    target_groups = elbv2_cli.describe_target_groups()
    for tg in target_groups['TargetGroups']:
        name = tg.get('TargetGroupName')
        if name is not None and name.startswith(AWS_RES_NAME):
            arn = tg.get('TargetGroupArn')
            if arn is None:
                raise RuntimeError('Target group ARN not found')
            logger.info(f"Deleting target group: {arn}")
            elbv2_cli.delete_target_group(TargetGroupArn=arn)


def delete_key_pair():
    try:
        key_pairs = ec2_res.key_pairs.filter(
            KeyNames=[AWS_KEY_PAIR_NAME],
        )
        for kp in key_pairs:
            logger.info(f"Deleting key pair: {kp}")
            kp.delete()
    except ClientError as e:
        error_code = get_error_code(e)
        if error_code != 'InvalidKeyPair.NotFound':
            raise


@backoff.on_exception(backoff.constant, ClientError, giveup=giveup)
def delete_security_groups():
    try:
        security_groups = ec2_res.security_groups.filter(
            GroupNames=[AWS_SECURITY_GROUP_NAME],
        )
        for sg in security_groups:
            logger.info(f"Deleting security group: {sg}")
            sg.delete()
    except ClientError as e:
        error_code = get_error_code(e)
        if error_code != 'InvalidGroup.NotFound':
            raise


def main():
    terminate_ec2()
    delete_lb()
    delete_target_groups()
    delete_key_pair()
    delete_security_groups()


if __name__ == '__main__':
    logging.basicConfig(level=LOG_LEVEL)
    main()
