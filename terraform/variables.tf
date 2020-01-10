
# %% General
variable "domain" {
  description = "Design domain of this service."
}

variable "environment" {
  description = "Environment Name"
}

variable "service_name" {
  description = "Name of the service"
}

variable "worker_scale_in_threshold" {
  description = "Threshold to trigger an autoscale-in activity, represented as number of messages in SQS"
  type        = number
}

variable "worker_scale_out_threshold" {
  description = "Threshold to trigger an autoscale-in activity, represented as number of messages in SQS"
  type        = number
}
