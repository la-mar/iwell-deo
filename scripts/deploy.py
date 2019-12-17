"""
Example docker deployment to AWS ECS cluster.

The script does the following:

    1. Loads environment variables from the .env

    For each service in SERVICES
    2. Generates a populated ECS task definition
        - You can configure your task definitions in the get_task_definition() method.
    3. Optionally authenticate Docker to ECR
    4. Optionally build any configured containers (see line ~480)
    5. Optionally push any configured containers to ECR
    6. Register the new task definition in ECR
    7. Retrieve the latest task definition revision number
    8. Update the running service with the new task definition and force a new deployment


This script assumes AWS credentials are stored in an environment variable suffixed with
the given environment name. I've found this to be the easiest way to deploy to different
AWS accounts with travis-ci.

    Ex: env_name = dev

        --- .env ---
        export AWS_ACCOUNT_ID=$AWS_ACCOUNT_ID_DEV
        export AWS_ACCESS_KEY_ID=$AWS_ACCESS_KEY_ID_DEV
        export AWS_SECRET_ACCESS_KEY=$AWS_SECRET_ACCESS_KEY_DEV
        ------------

    Ex: env_name = prod

        --- .env ---
        export AWS_ACCOUNT_ID=$AWS_ACCOUNT_ID_PROD
        export AWS_ACCESS_KEY_ID=$AWS_ACCESS_KEY_ID_PROD
        export AWS_SECRET_ACCESS_KEY=$AWS_SECRET_ACCESS_KEY_PROD
        ------------
"""


from typing import List, Dict, Union, Optional
import base64
import json
import os
import subprocess
import datetime
import sys

from dotenv import load_dotenv, dotenv_values
import boto3
import docker


# load_dotenv(f".env")


ENV = os.getenv("ENV", "prod")
PROJECT_NAME: str = os.getenv("COMPOSE_PROJECT_NAME")  # type: ignore
CLUSTER_NAME = os.getenv("ECS_CLUSTER")  # type: ignore
TASK_IAM_ROLE = "arn:aws:iam::864494265830:role/iwell-deo-task-role"

SERVICES: List[str] = ["iwell-worker", "iwell-cron"]

IMAGES = [
    {"name": PROJECT_NAME, "dockerfile": "Dockerfile", "build_context": "."},
    {
        "name": "iwell-redis-deo",
        "dockerfile": "./redis/Dockerfile",
        "build_context": "./redis",
    },
]

TAGS = [
    {"key": "domain", "value": "engineering"},
    {"key": "service_name", "value": PROJECT_NAME},
    {"key": "environment", "value": ENV},
    {"key": "terraform", "value": "true"},
]


BUILD = False
PUSH = False

print("\n\n" + "-" * 30)
print(f"ENV: {ENV}")
print(f"CLUSTER_NAME: {CLUSTER_NAME}")
print(f"SERVICES: {SERVICES}")
print("-" * 30 + "\n\n")


def get_task_definition(
    name: str,
    envs: dict,
    account_id: str,
    service_name: str,
    environment: str,
    image_name: str,
    tags: list = [],
    task_iam_role_arn: str = "ecsTaskExecutionRole",
):
    defs = {
        "iwell-worker": {
            "containerDefinitions": [
                {
                    "name": "iwell-worker",
                    "command": ["iwell", "run", "worker"],
                    "memoryReservation": 128,
                    "image": f"{account_id}.dkr.ecr.us-east-1.amazonaws.com/{image_name}:{environment}",
                    "essential": True,
                },
            ],
            "executionRoleArn": "ecsTaskExecutionRole",
            "family": f"{service_name}",
            "networkMode": "bridge",
            "taskRoleArn": task_iam_role_arn,
            "tags": tags,
            # "cpu": "512",  # from 128 CPU units (0.125 vCPUs) and 10240 CPU units (10 vCPUs)
        },
        "iwell-cron": {
            "containerDefinitions": [
                {
                    "name": "iwell-cron",
                    "command": ["iwell", "run", "cron", "--loglevel", "info"],
                    "memoryReservation": 128,
                    "image": f"{account_id}.dkr.ecr.us-east-1.amazonaws.com/{image_name}:{environment}",
                    "essential": True,
                },
            ],
            "executionRoleArn": "ecsTaskExecutionRole",
            "family": f"{service_name}",
            "networkMode": "bridge",
            "taskRoleArn": task_iam_role_arn,
            "tags": tags,
            # "cpu": "256",  # from 128 CPU units (0.125 vCPUs) and 10240 CPU units (10 vCPUs)
        },
    }

    return defs[name]


class AWSContainerInterface:
    ignore_env = False
    _env_name = None
    access_key_id = None
    secret_access_key = None
    region = None
    account_id = None
    _ecr = None
    _ecs = None
    cluster_name = None
    service_name = None
    _docker_client = None
    _docker_is_authorized = False

    def __init__(self, env_name: str = None, ignore_env: bool = False):
        self.ignore_env = ignore_env
        self._env_name = env_name
        self.credentials_from_profile()

    @property
    def docker_is_authorized(self):
        return self._docker_is_authorized

    @property
    def env_name(self):
        if not self.ignore_env:
            return os.getenv("ENV", self._env_name)
        else:
            return self._env_name

    @property
    def has_credentials(self):
        return all(
            [
                self.access_key_id is not None,
                self.secret_access_key is not None,
                self.region is not None,
                self.account_id is not None,
            ]
        )

    @property
    def ecr_url(self):
        if not self.has_credentials:
            self.credentials_from_profile()
        return f"{self.account_id}.dkr.ecr.{self.region}.amazonaws.com"

    @property
    def docker_client(self):
        return self._docker_client or self._get_docker_client()

    def credentials_from_profile(self, env_name: str = None):
        """Read AWS credentials from file.

        :param filename: Credentials filename, defaults to '.aws_credentials.json'
        :param filename: str, optional
        :return: Dictionary of AWS credentials.
        :rtype: Dict[str, str]
        """

        env_name = env_name or self.env_name

        credentials = {
            "access_key_id": os.getenv(f"AWS_ACCESS_KEY_ID"),
            "secret_access_key": os.getenv(f"AWS_SECRET_ACCESS_KEY"),
            "region": os.getenv(f"AWS_REGION", "us-east-1"),
            "account_id": os.getenv(f"AWS_ACCOUNT_ID"),
        }

        # print(credentials)
        [setattr(self, k, v) for k, v in credentials.items()]

        return credentials

    def get_client(self, service_name: str) -> "client":

        if not self.has_credentials:
            self.credentials_from_profile()

        return boto3.client(
            service_name,
            aws_access_key_id=self.access_key_id,
            aws_secret_access_key=self.secret_access_key,
            region_name=self.region,
        )

    def ecs(self):
        return self._ecs or self.get_client("ecs")

    def ecr(self):
        return self._ecr or self.get_client("ecr")

    def _get_docker_client(self, bypass_login: bool = False):

        # if not self.docker_is_authorized and bypass_login:
        docker_client = docker.DockerClient(base_url="unix:///var/run/docker.sock")

        # ecr_client = boto3.client('ecr', region_name=self.region)

        # token = ecr_client.get_authorization_token()

        # username, password = base64.b64decode(token['authorizationData'][0]['authorizationToken']).decode().split(':')
        # registry = token['authorizationData'][0]['proxyEndpoint']

        # print(docker_client.login(username, password, registry=registry, reauth=True))
        self._docker_login()

        return docker_client

    def _docker_login(self) -> str:
        """Authenticate to AWS in Docker

        Returns:
            dict -- credential mapping from get-login
        """
        os.environ["AWS_ACCOUNT_ID"] = self.account_id
        os.environ["AWS_ACCESS_KEY_ID"] = self.access_key_id
        os.environ["AWS_SECRET_ACCESS_KEY"] = self.secret_access_key
        credentials = (
            subprocess.check_output(["aws", "ecr", "get-login", "--no-include-email"])
            .decode("ascii")
            .strip()
        )

        message = os.popen(credentials).read()  # execute login in subprocess

        print(message)
        if "succeeded" in message.lower():
            self._docker_is_authorized = True

        # return credentials

    def update_service(self, cluster_name: str, service_name: str, force=True):

        # force new deployment of ECS service
        print(
            "\n\n"
            + f"{self.env_name} -- Forcing new deployment to ECS: {self.cluster_name}/{self.service_name}"
            + "\n\n"
        )
        response = self.ecs().update_service(
            cluster=cluster_name, service=service_name, forceNewDeployment=force
        )

        print("\n\n" + f"{self.env_name} -- Exiting ECS deployment update." + "\n\n")
        return self

    def update_task_definition(self):
        pass


class DockerImage:
    """ Image should be agnostic to its destination """

    build_context = "."
    dockerfile = "./Dockerfile"
    name = None
    image = None
    image_manager = None

    def __init__(
        self,
        image_manager: AWSContainerInterface,
        name: str = None,
        dockerfile: str = None,
        build_context: str = None,
        show_log: bool = False,
        tags: list = None,
    ):

        self.name = name
        self.image_manager = image_manager
        self.build_context = build_context or self.build_context
        self.dockerfile = dockerfile or self.dockerfile
        self.tags = self.default_tags + (tags or [])

    @property
    def commit_hash(self):
        return (
            subprocess.check_output(["git", "rev-parse", "--short", "HEAD"])
            .decode("ascii")
            .strip()
        )

    @property
    def build_date(self):
        return datetime.datetime.now().date()

    @property
    def default_tags(self):
        return [
            "latest",
            f"{self.build_date}",
            self.commit_hash,
            image_manager.env_name,
        ]

    @property
    def client(self):
        return self.image_manager.docker_client

    @property
    def repo_name(self):
        if isinstance(self.image_manager, AWSContainerInterface):
            return f"{self.image_manager.ecr_url}/{self.name}"
        else:
            return None  # docker hub url here

    def _logstream(self, source, stream_type: str):

        if stream_type == "build":
            while True:
                try:
                    output = next(source)
                    if "stream" in output.keys():
                        print(output["stream"].strip("\n"))
                    else:
                        print(output)
                except StopIteration:
                    break
                except ValueError:
                    print("Error parsing output from docker image build: %s" % output)

        elif stream_type == "push":
            for chunk in source.split("\r\n"):
                try:
                    if chunk:
                        d = json.loads(chunk)
                        print(d)

                except StopIteration:
                    break
                except ValueError:
                    print("Error parsing output from docker push to ECR: %s" % chunk)

    def build(self, show_log: bool = False):

        self.print_message(f"Building docker image: {self.name}")

        self.image, generator = self.client.images.build(
            path=self.build_context, dockerfile=self.dockerfile, tag=self.name
        )

        if show_log:
            self._logstream(generator, stream_type="build")

        self.print_message(f"Docker image build complete: {self.name}")

        return self

    def tag(self, name: str, tag: str):
        self.image.tag(name, tag=tag)
        return self

    def push(self, tag: str = None, show_log: bool = False):

        tag = tag or "latest"

        self.tag(self.repo_name, tag)

        self.print_message(f"Pushing to remote: {self.repo_name}")

        generator = self.client.images.push(self.repo_name, tag=tag)

        if show_log:
            self._logstream(generator, stream_type="push")

        self.print_message("Push complete")

        return self

    def print_message(self, message: str):
        print("\n" + "-" * 10 + f" {message} " + "-" * 10 + "\n")

    def deploy(
        self,
        tag: str = None,
        build: bool = True,
        push: bool = True,
        update_task=True,
        update_service=False,
        show_log: bool = False,
    ):

        if build:
            self.build(show_log=show_log)
        else:
            self.image = self.client.images.get(self.name)

        if push:
            self.push(show_log=show_log, tag=tag)

    def deploy_all(self, *args, **kwargs):
        for tag in self.tags:
            self.deploy(tag, *args, **kwargs)


image_manager = AWSContainerInterface(ENV)
# image_manager._docker_login()

# for image in IMAGES:
#     i = DockerImage(image_manager, **image)  # type: ignore
#     i.deploy_all(build=BUILD, push=PUSH, show_log=True)


client = image_manager.ecs()


def get_latest_revision(task_name: str):
    response = client.describe_task_definition(taskDefinition=task_name)
    return response["taskDefinition"]["revision"]


for service in SERVICES:
    print(f"{service}: Creating new task definition")
    cdef = get_task_definition(
        name=service,
        envs=task_envs,
        account_id=image_manager.account_id,  # type: ignore
        service_name=service,
        environment=ENV,
        image_name=PROJECT_NAME,
        tags=TAGS,
        task_iam_role_arn=TASK_IAM_ROLE,
    )
    print(f"{service}: Registering new revision in {image_manager.account_id}")
    client.register_task_definition(**cdef)

    rev_num = get_latest_revision(f"{service}")
    print(f"{service}: Updating service to {service}:{rev_num}")
    response = client.update_service(
        cluster=CLUSTER_NAME,
        service=service,
        forceNewDeployment=True,
        taskDefinition=f"{service}:{rev_num}",
    )
    print(f"{service}: Updated service to {service}:{rev_num}")

    # print(response)

