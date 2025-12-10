Kontox Golden Image – Standardized Base Image

The Kontox Golden Image is a standardized, security-vetted base container image used by all microservices in this project.
It ensures consistency, faster builds, reduced vulnerabilities, and simplified maintenance across the platform.

This Golden Image serves as the foundation for:

main-api

aux-service

It acts as a reliable, preconfigured Python environment optimized for running FastAPI-based microservices on AWS EKS.

1. Why Use a Golden Image?

Using a shared base image provides several advantages:

✔ Security

A single, hardened image allows central patching and reduces exposure to vulnerabilities.

✔ Consistency

All services have the same:

OS level dependencies

Python runtime

Base libraries

This removes “works on my machine” issues.

✔ Faster CI/CD Pipelines

Since most dependencies already exist in the Golden Image:

Docker builds require fewer steps

CI/CD pipeline runtime is reduced

✔ Easier maintenance

Updates to system packages or Python versions happen in one image, not dozens of microservices.

2. Contents of the Kontox Golden Image

The Golden Image includes:

Python 3.11 (or your chosen version)

FastAPI base dependencies

boto3 / AWS SDK

Uvicorn application server

Common OS packages:

ca-certificates

curl

wget

net-tools

Example minimal definition:

FROM python:3.11-slim

RUN apt-get update && \
    apt-get install -y --no-install-recommends curl wget && \
    pip install --no-cache-dir fastapi uvicorn boto3 && \
    rm -rf /var/lib/apt/lists/*


You can extend this as needed for production.

3. How Microservices Use the Golden Image

Both services use:

FROM kontox-goldenimage:latest


Then they only copy service-specific code:

COPY src/ /app/src
COPY requirements.txt .
RUN pip install -r requirements.txt


This keeps Dockerfiles small and maintainable.

4. How Golden Image Integrates Into CI/CD
During CI/CD:

GitHub Actions detects changes

Builds the service FROM the Golden Image

Produces a final service container

Pushes to ECR

Updates manifests with the new version

ArgoCD deploys it automatically

If the Golden Image changes:

Only the Golden Image is rebuilt

Microservices rebuild on top of it

This keeps everything consistent across environments.