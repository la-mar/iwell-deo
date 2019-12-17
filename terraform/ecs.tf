
### Task Definitions ###

data "aws_ecs_task_definition" "iwell_worker" {
  task_definition = "iwell-worker"
}

data "aws_ecs_task_definition" "iwell_cron" {
  task_definition = "iwell-cron"
}

### ECS Services ###
resource "aws_ecs_service" "iwell_worker" {
  name            = "iwell-worker"
  cluster         = data.terraform_remote_state.ecs_cluster.outputs.cluster_arn
  task_definition = data.aws_ecs_task_definition.iwell_worker.family

  scheduling_strategy     = "REPLICA"
  desired_count           = 2
  enable_ecs_managed_tags = true
  propagate_tags          = "TASK_DEFINITION"
  tags                    = local.tags

  # Optional: Allow external changes without Terraform plan difference
  lifecycle {
    ignore_changes = [
      desired_count,
      task_definition,
    ]
  }
}

module "worker_autoscaler" {
  source       = "./service_target_tracking"
  cluster_name = data.terraform_remote_state.ecs_cluster.outputs.cluster_name
  service_name = aws_ecs_service.iwell_worker.name
  min_capacity = 1
  max_capacity = 5
}

resource "aws_ecs_service" "iwell_cron" {
  name            = "iwell-cron"
  cluster         = data.terraform_remote_state.ecs_cluster.outputs.cluster_arn
  task_definition = data.aws_ecs_task_definition.iwell_cron.family

  scheduling_strategy     = "REPLICA"
  desired_count           = 1
  enable_ecs_managed_tags = true
  propagate_tags          = "TASK_DEFINITION"
  tags                    = local.tags

  # Optional: Allow external changes without Terraform plan difference
  lifecycle {
    ignore_changes = [
      desired_count,
      task_definition,
    ]
  }
}


# Define Task Role
resource "aws_iam_role" "ecs_task_role" {
  name               = "${var.service_name}-task-role"
  assume_role_policy = data.aws_iam_policy_document.task_policy.json
  tags               = local.tags
}

data "aws_iam_policy_document" "task_policy" {
  statement {
    sid    = ""
    effect = "Allow"
    actions = [
      "sts:AssumeRole",
    ]
    principals {
      type        = "Service"
      identifiers = ["ecs-tasks.amazonaws.com"]
    }
  }

}

resource "aws_iam_role_policy_attachment" "attach_ecs_service_policy_to_task_role" {
  role       = aws_iam_role.ecs_task_role.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AmazonEC2ContainerServiceforEC2Role"
}


# Allow task role to talk to SQS
data "aws_iam_policy_document" "allow_task_access_to_sqs" {
  statement {
    actions = [
      "sqs:*",
    ]

    resources = [
      aws_sqs_queue.celery.arn
    ]
  }

  statement {
    sid = "1" # task_access_secrets
    actions = [
      "ssm:GetParameter*",
    ]
    resources = [
      "arn:aws:ssm:*:*:parameter/${var.service_name}/*",
      "arn:aws:ssm:*:*:parameter/datadog/*"
    ]
  }

  statement {
    sid = "2" # task_access_kms
    actions = [
      "kms:ListKeys",
      "kms:ListAliases",
      "kms:Describe*",
      "kms:Decrypt"
    ]
    resources = [
      data.terraform_remote_state.kms.outputs.ssm_key_arn # dont use alias arn
    ]
  }

}

resource "aws_iam_policy" "allow_task_access_to_sqs" {
  name        = "${var.service_name}-task-access-sqs"
  path        = "/"
  description = "Allow ${var.service_name} tasks running in ECS to interface with SQS queues"

  policy = data.aws_iam_policy_document.allow_task_access_to_sqs.json
}

resource "aws_iam_role_policy_attachment" "attach_sqs_policy_to_task_role" {
  role       = aws_iam_role.ecs_task_role.name
  policy_arn = aws_iam_policy.allow_task_access_to_sqs.arn
}
