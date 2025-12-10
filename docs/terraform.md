Terraform – Infrastructure Overview

This project uses Terraform to define and manage all the AWS infrastructure that supports the microservices platform. Using Terraform gives us:

Consistency across environments

Version-controlled infrastructure

Repeatable, automated provisioning

Clear separation of responsibilities

The main components managed here are:

IAM roles for EKS workloads (IRSA)

IAM role for GitHub Actions (OIDC)

IAM roles for Secrets Store CSI

IAM role for the Cluster Autoscaler

(Optional) EKS cluster and node groups

1. Folder Structure

The Terraform code is organized as follows:

infra/terraform/
│
├── main.tf
├── providers.tf
├── variables.tf
├── outputs.tf
│
├── iam_github_actions.tf
├── iam_aux_service.tf
│
├── secrets-store-csi/
│     ├── iam.tf
│     └── data.tf
│
├── cluster-autoscaler/
│     ├── iam.tf
│     └── data.tf
│
└── eks/                     (optional)
      ├── cluster.tf
      ├── nodegroups.tf
      └── iam.tf


Each file/modules has a clear role, explained below.

2. providers.tf

This file configures the AWS provider. It sets:

AWS region

Authentication method

Required provider versions

Its purpose is simply to make sure Terraform is talking to the right AWS account and using compatible providers.

3. variables.tf

This file contains input variables used by the infrastructure.
Typical variables include:

Variable	Description
cluster_name	Name of the EKS cluster
aws_region	AWS region to deploy into
tags	Common resource tags

Using variables keeps the setup flexible and reusable between environments (dev/staging/prod).

4. outputs.tf

After Terraform applies, this file exposes useful information such as:

IAM role ARNs

OIDC provider ARN

Cluster-related outputs

These outputs are helpful for CI/CD pipelines or when configuring Kubernetes tooling.

5. main.tf

This is the “entry point” for the Terraform configuration.
It ties everything together by:

Calling IAM role definitions

Including CSI driver IAM settings

Including Cluster Autoscaler IAM

Optionally creating the EKS cluster and node groups

It doesn’t contain logic itself — it simply orchestrates the modules.

6. IAM Role for GitHub OIDC (iam_github_actions.tf)

This IAM role allows GitHub Actions to authenticate to AWS without using long-lived access keys.

The role:

Trusts GitHub’s OIDC provider

Allows GitHub workflows to assume the role

Grants permissions needed for CI/CD, such as:

Pushing images to ECR

Updating Kubernetes manifests

Using OIDC instead of static credentials is a major security best practice.

7. Aux-Service IAM Role (iam_aux_service.tf)

This file defines the IRSA role used by the aux-service deployment inside Kubernetes.

It provides only the minimum permissions required:

s3:ListBuckets

ssm:GetParameter*

secretsmanager:GetSecretValue

This ensures:

No hardcoded AWS credentials anywhere

Pod-level permission control

Least privilege principle is always applied

8. Secrets Store CSI IAM Role (secrets-store-csi/iam.tf)

This role allows the Secrets Store CSI Driver to pull secrets from AWS Secrets Manager.

It typically requires:

secretsmanager:GetSecretValue

kms:Decrypt (if using encrypted secrets)

This IAM setup directly supports the SecretProviderClass objects used by both microservices.

9. Cluster Autoscaler IAM Role (cluster-autoscaler/iam.tf)

The Cluster Autoscaler needs permissions to scale the underlying EC2 node groups.

The IAM role includes:

autoscaling:DescribeAutoScalingGroups

autoscaling:SetDesiredCapacity

autoscaling:TerminateInstanceInAutoScalingGroup

This allows Kubernetes to automatically add or remove nodes based on pod demand.

10. Optional EKS Module (eks/)

(Included in the repo but not required for the challenge)

This folder contains the configuration for provisioning a full EKS cluster:

cluster.tf

Creates:

The EKS control plane

Logging settings

The OIDC provider for IRSA

nodegroups.tf

Defines:

Node instance types

Scaling limits

AMI families

Attached IAM roles

iam.tf

Handles IAM roles required for:

Worker nodes

Bootstrapping

IRSA integration

This module is optional but included to show complete infrastructure capabilities.