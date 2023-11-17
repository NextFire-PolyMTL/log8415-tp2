import asyncio
import logging
import os
from contextlib import suppress

from deploy.bootstrap import bootstrap_instance, launch_orchestrator, launch_worker
from deploy.config import LOG_LEVEL
from deploy.infra import setup_infra
from orchestrator.containers import CONTAINERS_FILENAME, register_new_container
from orchestrator.utils import save_orchestrator_ip

logger = logging.getLogger(__name__)

async def main():
    logger.info("Setting up infrastructure")
    instances_m4 = await setup_infra()

    # Use this to use existing instance instead of creating new ones
    # instances = ec2_res.instances.filter(
    #     Filters=[
    #         {'Name': 'tag:Name', 'Values': [AWS_RES_NAME]},
    #         {'Name': 'instance-state-name', 'Values': ['pending', 'running']},
    #     ]
    # )

    logger.info("Bootstrapping workers and orchestrator")
    with suppress(FileNotFoundError):
        os.remove(CONTAINERS_FILENAME)

    tasks = []
    for inst in instances_m4[:-1]:
        tasks.append(asyncio.to_thread(bootstrap_instance, launch_worker, inst))
        register_new_container(inst.private_ip_address, "8000")
        register_new_container(inst.private_ip_address, "8001")
    await asyncio.gather(*tasks)

    last = instances_m4[-1]
    bootstrap_instance(launch_orchestrator, last)
    save_orchestrator_ip(last.public_ip_address)
    logger.info(f"ORCHESTRATOR public IP public ::: {last.public_ip_address}")



if __name__ == "__main__":
    logging.basicConfig(level=LOG_LEVEL)
    asyncio.run(main())
