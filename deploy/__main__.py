import asyncio
import logging

from deploy.bootstrap import bootstrap_instance
from deploy.config import LOG_LEVEL
from deploy.infra import setup_infra

logger = logging.getLogger(__name__)


async def main():
    logger.info('Setting up infrastructure')
    instances_m4, instances_t2 = await setup_infra()

    # Use this to use existing instance instead of creating new ones
    # instances = ec2_res.instances.filter(
    #     Filters=[
    #         {'Name': 'tag:Name', 'Values': [AWS_RES_NAME]},
    #         {'Name': 'instance-state-name', 'Values': ['pending', 'running']},
    #     ]
    # )

    logger.info('Bootstrapping instances')
    async with asyncio.TaskGroup() as tg:
        for inst in instances_m4:
            tg.create_task(
                asyncio.to_thread(bootstrap_instance, inst, '/cluster1'))
        for inst in instances_t2:
            tg.create_task(
                asyncio.to_thread(bootstrap_instance, inst, '/cluster2'))


if __name__ == '__main__':
    logging.basicConfig(level=LOG_LEVEL)
    asyncio.run(main())
