Architecture Overview – Kontaxa Cloud Platform

This document provides a clear, high-level explanation of the architecture used in the Kontaxa Cloud Engineering Challenge.
The goal is to describe how all components fit together across AWS, Kubernetes, CI/CD, and microservices.

The architecture is designed with:

Strong security (OIDC, IRSA, Secrets Manager)

Clean separation of responsibilities

Cloud-native best practices

Full automation using GitOps (Argo CD)

Simple and maintainable code

1. High-Level Architecture Diagram

The platform uses:

AWS EKS for running workloads

AWS IAM (IRSA) for pod-level permissions

GitHub Actions for CI/CD

Argo CD for GitOps deployment

AWS Secrets Manager for secure secrets

S3 + SSM for AWS operations

Prometheus/Grafana (optional monitoring)

📄 Diagram:
docs/architecture.png

2. Infrastructure Architecture (Terraform)

Terraform provisions:

OIDC IAM Role (GitHub Actions)

Allows GitHub to push to ECR and update manifests without AWS access keys.

IRSA Roles (main-api, aux-service, CSI Driver, Cluster Autoscaler)

Pods authenticate to AWS using IAM roles, not environment variables.

Optional EKS Cluster

Terraform can also create:

EKS control plane

Node groups

Worker IAM roles

Networking

Although optional, the Terraform structure supports full provisioning.

3. Kubernetes Architecture

The cluster contains several namespaces:

Namespace	Purpose
main-api	Hosts the public API service
aux-service	Hosts the AWS integration service
argocd	GitOps controller and UI
monitoring	Prometheus/Grafana (optional)
kube-system	Cluster controllers, metrics, autoscaler

Each application namespace contains:

Deployment

Service (ClusterIP)

ConfigMap (version)

SecretProviderClass (Secrets Manager)

HPA (Horizontal Pod Autoscaler)

This structure keeps everything organized, isolated, and easy to scale.

4. Microservices Architecture

The system uses a two-service architecture:

main-api

Public entry point

Handles routing

Adds version metadata

Calls aux-service for AWS operations

Never communicates with AWS directly

aux-service

Internal-only service

Handles S3 bucket listing

Handles SSM parameter retrieval

Reads secrets from Secrets Manager

Uses IRSA IAM permissions

Internal communication uses Kubernetes DNS:

http://aux-service.aux-service.svc.cluster.local:8000


This keeps the architecture secure and modular.

5. Secrets Architecture

Secrets never touch Kubernetes Secret objects.

Instead:

AWS Secrets Manager

Stores sensitive values, e.g., database passwords, API keys.

Secrets Store CSI Driver

Runs inside Kubernetes and fetches secrets securely.

SecretProviderClass

Defines which secrets to mount and how.

IRSA

Ensures pods access AWS Secrets Manager with AWS IAM, not static keys.

Secrets appear inside pods as files:

/mnt/secrets-store/<key-name>


This approach avoids secret leakage and centralizes operations in AWS.

6. CI/CD + GitOps Architecture

This architecture intentionally separates CI/CD from deployment:

CI/CD (GitHub Actions) Responsibilities

Build Docker images

Push to Amazon ECR

Update Kubernetes manifests

Update version ConfigMaps

Commit changes back to Git

GitHub authenticates to AWS using OIDC, so no AWS keys are stored anywhere.

GitOps (Argo CD) Responsibilities

Watch the Git repo

Detect manifest changes

Deploy changes to EKS

Ensure the cluster matches Git (drift correction)

Provide UI for deployments and rollbacks

This GitOps model ensures:

Predictable deployments

Easy rollbacks

Full audit history

No direct kubectl deployments

7. Autoscaling Architecture

Two layers of autoscaling exist:

1. Horizontal Pod Autoscaler (HPA)

Configured for both services:

Scales pods based on CPU/memory

Ensures stable workloads under load

2. Cluster Autoscaler

Scales EKS nodes as pods require more capacity.

IAM permissions allow it to modify Auto Scaling Groups securely.

8. Monitoring Architecture

The optional monitoring namespace provides:

Prometheus (metrics collection)

Grafana (dashboards)

Node Exporter

Kube-State-Metrics

This gives full visibility into:

Pod health

Node performance

Autoscaler behavior

API performance

Resource saturation

9. Why This Architecture Was Chosen
Security

No AWS keys in GitHub

No secrets in Kubernetes

Pod-level IAM permissions

Namespaced isolation

Scalability

Independent autoscaling for each service

Cluster autoscaler responds to changes automatically

Maintainability

Clear service boundaries

Declarative infrastructure and manifests

Automatic GitOps deployment

Modern Cloud-Native Practices

OIDC, IRSA, GitOps, CSI Driver

Kubernetes microservices

Infrastructure as Code

This architecture is not only correct for the challenge but also production-ready.