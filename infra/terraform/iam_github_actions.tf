########################################
# IAM for GitHub Actions (OIDC)
########################################

# Example: github_org = "your-github-org", github_repo = "kantox-cloud-challenge"
variable "github_org" {
  description = "GitHub organization or user that owns the repo"
  type        = string
}

variable "github_repo" {
  description = "GitHub repository name (without org)"
  type        = string
}

# Optional: restrict which branches/tags can assume the role
# Example: "ref:refs/heads/main"
variable "github_ref_pattern" {
  description = "Allowed GitHub ref (branch/tag) for assuming the role"
  type        = string
  default     = "ref:refs/heads/main"
}

# -------------------------
# OIDC Provider for GitHub Actions
# -------------------------
resource "aws_iam_openid_connect_provider" "github" {
  url = "https://token.actions.githubusercontent.com"

  client_id_list = [
    "sts.amazonaws.com"
  ]

  thumbprint_list = [
    # GitHub Actions OIDC root CA thumbprint
    "6938fd4d98bab03faadb97b34396831e3780aea1"
  ]
}

# -------------------------
# IAM Role assumed by GitHub Actions via OIDC
# -------------------------

data "aws_iam_policy_document" "github_actions_assume_role" {
  statement {
    effect = "Allow"

    principals {
      type        = "Federated"
      identifiers = [aws_iam_openid_connect_provider.github.arn]
    }

    actions = ["sts:AssumeRoleWithWebIdentity"]

    condition {
      test     = "StringEquals"
      variable = "token.actions.githubusercontent.com:aud"
      values   = ["sts.amazonaws.com"]
    }

    # Restrict to this repo and ref
    condition {
      test     = "StringLike"
      variable = "token.actions.githubusercontent.com:sub"
      values = [
        "repo:${var.github_org}/${var.github_repo}:${var.github_ref_pattern}"
      ]
    }
  }
}

# Permissions for GitHub Actions (narrow to what you need)
# For example: allow it to update SSM parameters and maybe manage ECR in future.
data "aws_iam_policy_document" "github_actions_policy_doc" {
  statement {
    sid = "SSMParametersReadWrite"
    actions = [
      "ssm:GetParameter",
      "ssm:GetParameters",
      "ssm:GetParametersByPath",
      "ssm:DescribeParameters",
      "ssm:PutParameter"
    ]
    resources = [
      "arn:aws:ssm:${var.aws_region}:${var.aws_account_id}:parameter/${var.project}/${var.environment}/*"
    ]
  }

  # You can add more statements later for ECR / S3 / etc.
}

resource "aws_iam_policy" "github_actions_policy" {
  name        = "${local.name_prefix}-github-actions-policy"
  description = "Permissions for GitHub Actions pipelines"
  policy      = data.aws_iam_policy_document.github_actions_policy_doc.json
}

resource "aws_iam_role" "github_actions_role" {
  name               = "${local.name_prefix}-github-actions-role"
  assume_role_policy = data.aws_iam_policy_document.github_actions_assume_role.json

  tags = local.common_tags
}

resource "aws_iam_role_policy_attachment" "github_actions_attach" {
  role       = aws_iam_role.github_actions_role.name
  policy_arn = aws_iam_policy.github_actions_policy.arn
}

output "github_actions_role_arn" {
  description = "IAM Role ARN for GitHub Actions OIDC"
  value       = aws_iam_role.github_actions_role.arn
}
