variable "aws_region" {
  description = "AWS region to deploy to"
  type        = string
  default     = "us-west-1"
}

variable "project" {
  description = "Project name used for resource naming"
  type        = string
  default     = "kantox-cloud-challenge"
}

variable "environment" {
  description = "Environment name (e.g. dev, staging, prod)"
  type        = string
  default     = "dev"
}
