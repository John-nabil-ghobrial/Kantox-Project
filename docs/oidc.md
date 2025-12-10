OIDC Authentication – GitHub Actions to AWS

This document explains the OpenID Connect (OIDC) trust relationship between GitHub and AWS used to authenticate CI/CD without long-lived AWS credentials.

1. Why Use OIDC?

OIDC removes the need for storing AWS access keys in GitHub.

Benefits:

More secure

No secret rotation

Least privilege

Temporary credentials per workflow

Perfect for CI/CD pipelines

2. How It Works

GitHub Actions requests a signed OIDC token

AWS IAM verifies:

Repo name

Branch name

Workflow file

AWS generates temporary credentials

GitHub Actions assumes the IAM role

CI/CD uses AWS APIs (ECR push, etc.)

3. IAM Role Setup

Terraform creates the role with:

Trust policy for GitHub OpenID provider

Conditions limiting access to:

Specific repo

Specific branch

Specific workflow

Permissions include:

ecr:PutImage

ecr:BatchCheckLayerAvailability

Optional S3/SSM access for testing

4. GitHub Workflow Configuration
permissions:
  id-token: write
  contents: write


Then:

uses: aws-actions/configure-aws-credentials@v4
with:
  role-to-assume: arn:aws:iam::<ACCOUNT>:role/github-oidc-role
  aws-region: us-east-1

5. Security Controls

The IAM role is restricted by:

Repository name

Branch name

Subject claim

Workflow file