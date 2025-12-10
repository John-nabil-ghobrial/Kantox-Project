GitHub OIDC – AWS Authentication Guide

This project uses GitHub OpenID Connect (OIDC) to let GitHub Actions authenticate with AWS without using access keys.
This is the modern, secure, recommended method by both AWS and GitHub.

Using OIDC removes the need for:

Storing AWS_ACCESS_KEY_ID

Storing AWS_SECRET_ACCESS_KEY

Rotating IAM keys

Instead, GitHub Actions obtains a short-lived token during every run.

1. Why OIDC Is Used

OIDC provides several benefits:

✔ No long-term AWS credentials

Nothing stored in GitHub Secrets.

✔ Fine-grained IAM permissions

The GitHub role can only do what Terraform permits.

✔ Automatic key rotation

Tokens expire after the job ends.

✔ Safer for CI/CD

No risk of key exposure, ever.

This aligns perfectly with best practices for cloud security.

2. How OIDC Authentication Works (Simple Explanation)

A GitHub Action workflow starts.

GitHub provides a signed OIDC token to the workflow.

AWS verifies:

The token signature

The repository

The branch

If valid, AWS allows the workflow to assume the IAM role defined in Terraform.

The workflow receives temporary AWS credentials.

No keys.
No rotation.
No manual secrets.

3. Terraform Role for GitHub (iam_github_actions.tf)

Terraform creates an IAM role that GitHub Actions can assume.

The trust policy allows:

GitHub’s OIDC provider

A specific repository

A specific branch or environment

The role typically includes permissions like:

ecr:BatchGetImage, ecr:PutImage

eks:DescribeCluster

Optionally update manifests (if needed)

Example actions granted:

- Pushing to ECR
- Pulling from ECR
- Reading cluster info


This role is intentionally restricted to maintain least-privilege access.

4. GitHub Workflow Usage

Inside each CI/CD workflow file (main-api-ci-cd.yaml, aux-service-ci-cd.yaml), AWS authentication happens with this step:

- name: Configure AWS credentials
  uses: aws-actions/configure-aws-credentials@v2
  with:
    role-to-assume: arn:aws:iam::123456:role/github-oidc-role
    aws-region: ${{ env.AWS_REGION }}


After this step:

The workflow can push images to ECR

No secrets are required

The workflow only has permissions for tasks defined in Terraform

5. AWS Console Steps (If Setting Up Manually)

If someone needed to recreate the role manually, the steps would be:

Open IAM → Identity providers → Add provider

Choose OpenID Connect


Create IAM role with trust relationship for GitHub

Restrict it to your repository

Attach needed policies (ECR, etc.)

However, in this project Terraform fully automates this.

6. Summary

With OIDC:

GitHub Actions authenticates securely

No AWS keys are ever stored

Permissions are tightly controlled

The CI/CD pipeline becomes safer and easier to manage

Terraform sets everything up, and GitHub Actions simply assumes the role during builds and deployments.

This creates a clean, modern, and secure authentication flow for all CI/CD operations.
