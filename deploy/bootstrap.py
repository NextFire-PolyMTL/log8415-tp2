import io
import logging
import tarfile
from typing import TYPE_CHECKING, Callable

import backoff
from paramiko import AutoAddPolicy, RSAKey, SSHClient, ssh_exception

from deploy.config import AWS_KEY_PAIR_NAME, SSH_USERNAME
from deploy.utils import SSHExecError, ssh_exec

if TYPE_CHECKING:
    from mypy_boto3_ec2.service_resource import Instance

logger = logging.getLogger(__name__)


@backoff.on_exception(backoff.constant,
                      (ssh_exception.NoValidConnectionsError, TimeoutError))
def bootstrap_instance(launch_app: Callable[['Instance', SSHClient], None], instance: 'Instance'):
    logger.info(f"Bootstrapping {instance=}")
    ssh_key = RSAKey.from_private_key_file(f'{AWS_KEY_PAIR_NAME}.pem')
    with SSHClient() as ssh_client:
        ssh_client.set_missing_host_key_policy(AutoAddPolicy())
        ssh_client.connect(
            hostname=instance.public_ip_address,
            username=SSH_USERNAME,
            pkey=ssh_key,
        )
        _setup_docker(ssh_client)
        launch_app(instance, ssh_client)


@backoff.on_exception(backoff.constant, SSHExecError)
def _setup_docker(ssh_client: SSHClient):
    logger.info('Setting up docker')
    ssh_exec(ssh_client, r'sudo snap install docker')


@backoff.on_exception(backoff.constant, SSHExecError)
def launch_worker(instance: 'Instance', ssh_client: SSHClient):
    logger.info('Pushing sources')
    with ssh_client.open_sftp() as sftp:
        with io.BytesIO() as f:
            with tarfile.open(fileobj=f, mode='w:gz') as tar:
                tar.add('pyproject.toml')
                tar.add('poetry.lock')
                tar.add('worker/')
                tar.add('.docker/worker.Dockerfile')
                tar.add('.docker/worker.docker-compose.yml')
            f.seek(0)
            sftp.putfo(f, 'src.tar.gz')
    logger.info('Build and start worker')
    ssh_exec(
        ssh_client, rf"""
            rm -rf src && mkdir -p src
            tar xzf src.tar.gz -C src/
            cd src/
            sudo INSTANCE_ID={instance.id} docker compose -f .docker/worker.docker-compose.yml up --build -d
            """)


@backoff.on_exception(backoff.constant, SSHExecError)
def launch_orchestrator(instance: 'Instance', ssh_client: SSHClient):
    logger.info('Pushing sources')
    with ssh_client.open_sftp() as sftp:
        with io.BytesIO() as f:
            with tarfile.open(fileobj=f, mode='w:gz') as tar:
                tar.add('pyproject.toml')
                tar.add('poetry.lock')
                tar.add('orchestrator/')
                tar.add('.docker/orchestrator.Dockerfile')
            f.seek(0)
            sftp.putfo(f, 'src.tar.gz')
    logger.info('Building orchestrator')
    ssh_exec(
        ssh_client, r"""
            rm -rf src && mkdir -p src
            tar xzf src.tar.gz -C src/
            cd src/
            sudo docker build -t orchestrator -f .docker/orchestrator.Dockerfile .
            """)
    logger.info('Start orchestrator')
    ssh_exec(
        ssh_client,
        rf"""
        sudo docker rm -f orchestrator
        sudo docker run --name orchestrator -d -p 80:8000 \
            -e INSTANCE_ID={instance.id} \
            orchestrator
        """)
