from typing import Union

import boto3
import requests

# from botocore.exceptions import NoRegionError

from util.itertools_ import query


def get_ecs_task_meta():
    return requests.get(
        "http://169.254.169.254/latest/dynamic/instance-identity/document"
    ).json()


def get_message_count(queue_name: str, region_name: str = None) -> Union[int, None]:

    region_name = region_name or get_ecs_task_meta().get("region")
    client = boto3.client("sqs", region_name=region_name)
    queue_url = None
    message_count = None

    queues = client.list_queues(QueueNamePrefix=queue_name)["QueueUrls"]
    if len(queues) > 0:
        queue_url = queues[0]

    if queue_url is not None:
        response = client.get_queue_attributes(
            QueueUrl=queue_url, AttributeNames=["ApproximateNumberOfMessages"]
        )

        message_count = int(
            query("Attributes.ApproximateNumberOfMessages", data=response) or 0
        )
    return message_count
