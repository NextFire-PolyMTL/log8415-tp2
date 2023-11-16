import asyncio
import logging

from deploy.bootstrap import bootstrap_instance, launch_orchestrator, launch_worker
from deploy.config import LOG_LEVEL
from deploy.infra import setup_infra
from orchestrator.containers import register_new_container

logger = logging.getLogger(__name__)


async def main():
    logger.info('Setting up infrastructure')
    instances_m4 = await setup_infra()

    # Use this to use existing instance instead of creating new ones
    # instances = ec2_res.instances.filter(
    #     Filters=[
    #         {'Name': 'tag:Name', 'Values': [AWS_RES_NAME]},
    #         {'Name': 'instance-state-name', 'Values': ['pending', 'running']},
    #     ]
    # )

    logger.info('Bootstrapping workers')
    async with asyncio.TaskGroup() as tg:
        for inst in instances_m4[:-1]:
            tg.create_task(
                asyncio.to_thread(bootstrap_instance, launch_worker, inst))

        logger.info('Bootstrapping orchestrator')
        logger.info(
            f'ORCHESTRATOR public IP public ::: {instances_m4[-1].public_ip_address}')
        bootstrap_instance(launch_orchestrator, instances_m4[-1])

    logger.info('Registering workers')
    for inst in instances_m4[:-1]:
        logger.info(f'Registering private IP {inst.public_ip_address}')
        register_new_container(inst.public_ip_address, '8000')
        register_new_container(inst.public_ip_address, '8001')


if __name__ == '__main__':
    logging.basicConfig(level=LOG_LEVEL)
    asyncio.run(main())
