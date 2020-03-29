
### Task Definitions ###

data "aws_ecs_task_definition" "iwell_web" {
  task_definition = "iwell-web"
}

data "aws_ecs_task_definition" "iwell_worker" {
  task_definition = "iwell-worker"
}

data "aws_ecs_task_definition" "iwell_cron" {
  task_definition = "iwell-cron"
}

resource "aws_security_group" "iwell_web" {
  description = "Security group for ${var.service_name}"

  vpc_id = data.terraform_remote_state.vpc.outputs.vpc_id
  name   = "${var.service_name}-web-sg"
  tags   = merge(local.tags, { Name = var.service_name })

  ingress {
    description = "All TCP Traffic"
    protocol    = "tcp"
    from_port   = var.service_port
    to_port     = var.service_port
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    description = "All Traffic"
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}


### ECS Services ###
resource "aws_ecs_service" "iwell_web" {
  name            = "iwell-web"
  cluster         = data.terraform_remote_state.web_cluster.outputs.cluster_arn
  task_definition = data.aws_ecs_task_definition.iwell_web.family

  scheduling_strategy = "REPLICA"
  ordered_placement_strategy {
    type  = "spread"
    field = "instanceId"
  }
  desired_count           = 1
  enable_ecs_managed_tags = true
  propagate_tags          = "TASK_DEFINITION"
  tags                    = local.tags

  # allow external changes without Terraform plan difference
  lifecycle {
    create_before_destroy = true
    ignore_changes = [
      desired_count,
      task_definition,
    ]
  }

  network_configuration {
    subnets          = data.terraform_remote_state.vpc.outputs.private_subnets
    security_groups  = [aws_security_group.iwell_web.id]
    assign_public_ip = false
  }

  service_registries {
    registry_arn   = aws_service_discovery_service.web.arn
    container_name = "iwell-web"

  }
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
  source              = "./service_target_tracking"
  cluster_name        = data.terraform_remote_state.ecs_cluster.outputs.cluster_name
  service_name        = aws_ecs_service.iwell_worker.name
  min_capacity        = 2
  max_capacity        = 5
  queue1              = "iwell-celery"
  scale_in_threshold  = var.worker_scale_in_threshold
  scale_out_threshold = var.worker_scale_out_threshold
  scale_in_cooldown   = var.worker_scale_in_cooldown
  scale_out_cooldown  = var.worker_scale_out_cooldown
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
data "aws_iam_policy_document" "task_policy_attachment" {
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

resource "aws_iam_policy" "task_policy_attachment" {
  name        = "${var.service_name}-task-policy"
  path        = "/"
  description = "Allow ${var.service_name} tasks running in ECS to interface with SQS queues"

  policy = data.aws_iam_policy_document.task_policy_attachment.json
}

resource "aws_iam_role_policy_attachment" "attach_sqs_policy_to_task_role" {
  role       = aws_iam_role.ecs_task_role.name
  policy_arn = aws_iam_policy.task_policy_attachment.arn
}
