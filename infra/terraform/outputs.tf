output "s3_app_bucket_name" {
  description = "Name of the application S3 bucket"
  value       = aws_s3_bucket.app.bucket
}

output "ssm_parameter_example_name" {
  description = "Example SSM parameter path"
  value       = aws_ssm_parameter.app_config_example.name
}
