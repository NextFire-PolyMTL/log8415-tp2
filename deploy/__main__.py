import asyncio
import logging

from deploy.bootstrap import bootstrap_instance, launch_orchestrator, launch_worker
from deploy.config import LOG_LEVEL
from deploy.infra import setup_infra
from 

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
        bootstrap_instance(launch_orchestrator, instances_m4[-1])

        logger.info('Registering workers')
        register_new_container(ip: str, port: str) 


if __name__ == '__main__':
    logging.basicConfig(level=LOG_LEVEL)
    asyncio.run(main())
