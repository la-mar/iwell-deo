resource "aws_sqs_queue" "celery" {
  name                       = "iwell-celery"
  delay_seconds              = 0
  message_retention_seconds  = 360
  receive_wait_time_seconds  = 0
  visibility_timeout_seconds = 120

  tags = local.tags
}

resource "aws_sqs_queue_policy" "sqs" {
  queue_url = aws_sqs_queue.celery.id
  policy    = data.aws_iam_policy_document.allow_ecs_access_to_sqs.json

}

data "aws_iam_policy_document" "allow_ecs_access_to_sqs" {
  statement {

    principals {
      type = "Service"
      identifiers = [
        "ecs.amazonaws.com",
      ]
    }

    actions = [
      "sqs:*",
    ]

    resources = [
      aws_sqs_queue.celery.arn
    ]

    condition {
      test     = "ArnEquals"
      variable = "ecs:service"
      values   = [aws_ecs_service.iwell_worker.id, aws_ecs_service.iwell_cron.id]
    }

  }
}

