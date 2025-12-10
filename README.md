Kontaxa – Cloud Engineering Challenge

This repository contains the complete end-to-end solution for the Kontaxa Cloud Engineering Challenge, including:

 Microservices architecture (main-api + aux-service)

️ AWS Infrastructure (Terraform)

️ Kubernetes (EKS) deployments

 Secrets Management (AWS Secrets Manager + CSI Driver)

 GitOps using Argo CD

 CI/CD using GitHub Actions + OIDC

 Monitoring namespace (Prometheus + Grafana)

 API testing documentation

 Complete application code

Everything in this repository is built using production-ready practices and fully documented.

 1. Architecture Overview

The system is composed of two microservices:

main-api

Public-facing API

Delegates AWS operations to aux-service

Adds version metadata to every response

Communicates internally within the EKS cluster

aux-service

Handles AWS S3 + SSM Parameter Store

Uses IRSA pod-level IAM roles

Injects secrets using AWS Secrets Manager

Returns its own version metadata

Platform Components

AWS EKS

AWS IAM + IRSA

AWS Secrets Manager

Secrets Store CSI Driver

Cluster Autoscaler

Metrics Server

NGINX Ingress

Argo CD GitOps

GitHub OIDC CI/CD

 Architecture Diagram:
docs/architecture.png

 Deployment Guide:
docs/deployment-guide.md

️ 2. Infrastructure (Terraform)

Terraform provisions:

IAM Role for GitHub OIDC → CI/CD access

IAM Roles for Service Accounts (IRSA)

main-api (optional)

aux-service (S3 + SSM access)

IAM for Secrets Store CSI Driver

IAM for Cluster Autoscaler

Optional EKS Cluster definition

Terraform code is under:

infra/terraform/


 Full documentation:
docs/terraform.md

️ 3. Kubernetes Manifests

Application manifests:

infra/k8s/apps/main-api/
infra/k8s/apps/aux-service/


Each service includes:

deployment.yaml

service.yaml (ClusterIP)

configmap.yaml (versioning)

secretproviderclass.yaml (Secrets Manager)

hpa.yaml (autoscaling)

Synchronization is managed by Argo CD.

 4. GitOps with Argo CD

Argo CD watches the following paths:

infra/k8s/apps/main-api
infra/k8s/apps/aux-service


Argo CD provides:

Automatic sync

Drift detection

Rollout visualization

Git-driven deployments

Argo CD configuration:

infra/k8s/argocd/


 Documentation: docs/argocd.md

 5. Secrets Management

We use:

AWS Secrets Manager → stores application secrets

Secrets Store CSI Driver → injects secrets into pods

SecretProviderClass → maps Secrets Manager → Kubernetes volume

Secrets never appear in Git or environment variables.

 Documentation: docs/secrets-manager.md

 6. CI/CD Pipeline (GitHub Actions + OIDC)

Each service has its own pipeline:

.github/workflows/main-api-ci-cd.yaml
.github/workflows/aux-service-ci-cd.yaml


Pipeline steps:

Authenticate to AWS using OIDC

Build docker image

Push image to ECR

Update Kubernetes manifest with new image tag

Commit changes back to repo

ArgoCD detects change → deploys automatically

 CI/CD documentation:
docs/cicd.md

 OIDC configuration:
docs/oidc.md

 7. Monitoring Namespace (Optional Requirement)

Monitoring components live under:

infra/k8s/monitoring/


Recommended stack:

Prometheus

Grafana

Node Exporter

Kube-State-Metrics

Installed via the Helm chart: kube-prometheus-stack.

 Documentation:
docs/monitoring.md

 8. Microservices Code

Code is located in:

services/main-api/
services/aux-service/

main-api:

Routes requests

Calls aux-service

Adds version metadata

Health endpoints

aux-service:

Calls AWS S3 (list_buckets())

Calls AWS SSM (get_parameter())

Uses IRSA and boto3

Provides health + version

Version injected using ConfigMaps → environment variables.

 9. API Testing

API Testing commands (curl examples) include:

/health

/version

/buckets

/parameters

/parameters/{name}

Testing guide:

 docs/api-testing.md

Test results

 docs/images/

 10. Documentation Index

  11. Golden Image Standardization

All microservices in this project are built on top of a shared Kontox Golden Image.
This base image provides:

Python runtime

FastAPI dependencies

AWS SDK (boto3)

Common OS packages

Hardened, minimal footprint

Using a shared Golden Image ensures:

Consistency across all services

Reduced build times in CI/CD

Centralized updates

Easier security patching

Both services (main-api and aux-service) inherit from:

FROM kontox-goldenimage:latest
All documentation lives under:

docs/


Includes:

terraform.md

argocd.md

cicd.md

oidc.md

monitoring.md

secrets-manager.md

deployment-guide.md

api-testing.md

Architecture diagram
