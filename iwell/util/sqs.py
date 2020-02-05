from typing import Union

import boto3
from util.itertools_ import query


def get_message_count(queue_name: str) -> Union[int, None]:
    client = boto3.client("sqs")
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

