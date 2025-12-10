

variable "aws_account_id" {
  description = "AWS account ID where resources are created"
  type        = string
}

# EKS OIDC issuer URL, e.g.
# oidc.eks.us-west-1.amazonaws.com/id/ABCDEFG123456789
variable "eks_oidc_issuer_url" {
  description = "OIDC issuer URL for the EKS cluster (without https://)"
  type        = string
}

# Kubernetes service account that Aux Service will use
variable "aux_service_sa_name" {
  description = "K8s service account name for aux service"
  type        = string
  default     = "aux-service-sa"
}

variable "aux_service_sa_namespace" {
  description = "K8s namespace for aux service"
  type        = string
  default     = "aux-service"
}

locals {
  aux_service_ssm_arn_prefix = "arn:aws:ssm:${var.aws_region}:${var.aws_account_id}:parameter/${var.project}/${var.environment}"
}

# -------------------------
# IAM Policy for Aux Service
# -------------------------
data "aws_iam_policy_document" "aux_service_policy_doc" {
  statement {
    sid = "ListAllBuckets"
    actions = [
      "s3:ListAllMyBuckets"
    ]
    resources = ["*"]
  }

  statement {
    sid = "ListProjectBucket"
    actions = [
      "s3:ListBucket"
    ]
    resources = [
      aws_s3_bucket.app.arn
    ]
  }

  statement {
    sid = "ReadParameters"
    actions = [
      "ssm:GetParameter",
      "ssm:GetParameters",
      "ssm:GetParametersByPath",
      "ssm:DescribeParameters"
    ]
    resources = [
      "${local.aux_service_ssm_arn_prefix}/*"
    ]
  }
}

resource "aws_iam_policy" "aux_service_policy" {
  name        = "${local.name_prefix}-aux-service-policy"
  description = "Permissions for Aux Service to read S3 buckets and SSM parameters"
  policy      = data.aws_iam_policy_document.aux_service_policy_doc.json
}

# -------------------------
# IAM Role for Aux Service (IRSA)
# -------------------------
data "aws_iam_policy_document" "aux_service_assume_role" {
  statement {
    effect  = "Allow"
    actions = ["sts:AssumeRoleWithWebIdentity"]

    principals {
      type        = "Federated"
      identifiers = [
        "arn:aws:iam::${var.aws_account_id}:oidc-provider/${var.eks_oidc_issuer_url}"
      ]
    }

    condition {
      test     = "StringEquals"
      # key like: oidc.eks.eu-west-1.amazonaws.com/id/XYZ123:sub
      variable = "${var.eks_oidc_issuer_url}:sub"
      values = [
        "system:serviceaccount:${var.aux_service_sa_namespace}:${var.aux_service_sa_name}"
      ]
    }
  }
}

resource "aws_iam_role" "aux_service_role" {
  name               = "${local.name_prefix}-aux-service-role"
  assume_role_policy = data.aws_iam_policy_document.aux_service_assume_role.json

  tags = local.common_tags
}

resource "aws_iam_role_policy_attachment" "aux_service_attach" {
  role       = aws_iam_role.aux_service_role.name
  policy_arn = aws_iam_policy.aux_service_policy.arn
}

output "aux_service_role_arn" {
  description = "IAM role ARN to attach to Aux Service service account via IRSA"
  value       = aws_iam_role.aux_service_role.arn
}
