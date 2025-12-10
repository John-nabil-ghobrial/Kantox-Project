locals {
  common_tags = {
    Project     = var.project
    Environment = var.environment
    ManagedBy   = "terraform"
  }

  name_prefix = "${var.project}-${var.environment}"
}

# -------------------------
# S3 bucket (for example: app data / artifacts)
# -------------------------
resource "aws_s3_bucket" "app" {
  bucket        = "${local.name_prefix}-app-bucket"
  force_destroy = true

  tags = local.common_tags
}

resource "aws_s3_bucket_versioning" "app" {
  bucket = aws_s3_bucket.app.id

  versioning_configuration {
    status = "Enabled"
  }
}

resource "aws_s3_bucket_server_side_encryption_configuration" "app" {
  bucket = aws_s3_bucket.app.id

  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }
}

# -------------------------
# SSM Parameter Store – example parameters
# -------------------------

# Root path for your app's config in Parameter Store
resource "aws_ssm_parameter" "app_config_example" {
  name  = "/${var.project}/${var.environment}/example"
  type  = "String"
  value = "example-value"

  tags = local.common_tags
}

# Parameter where you could store aux-service version, for example
resource "aws_ssm_parameter" "aux_service_version" {
  name  = "/${var.project}/${var.environment}/aux-service/version"
  type  = "String"
  value = "1.0.0"

  tags = local.common_tags
}

# Parameter where you could store main-api version if you want
resource "aws_ssm_parameter" "main_api_version" {
  name  = "/${var.project}/${var.environment}/main-api/version"
  type  = "String"
  value = "1.0.0"

  tags = local.common_tags
}
