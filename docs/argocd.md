rgo CD – GitOps Deployment Guide

Argo CD is used in this project to manage all Kubernetes deployments using a GitOps workflow.
The idea is simple: the Git repository becomes the source of truth, and Argo CD keeps the cluster synced with what is committed to Git.

This ensures:

Consistent deployments

Predictable rollouts

Easy rollbacks

Full visibility into cluster state

Self-healing when someone changes something manually

1. How Argo CD Is Installed

Argo CD is installed using a small Kustomize wrapper rather than embedding the full YAML in our repo.
This keeps everything clean and up-to-date.

Folder:

infra/k8s/argocd/


Files:

namespace.yaml – creates the argocd namespace

kustomization.yaml – references the official Argo CD install manifest

Kustomization content:

apiVersion: kustomize.config.k8s.io/v1beta1
kind: Kustomization

namespace: argocd

resources:
  - https://raw.githubusercontent.com/argoproj/argo-cd/stable/manifests/install.yaml


To apply:

kubectl apply -k infra/k8s/argocd/

2. Argo CD Applications

Each microservice has its own Argo CD Application:

infra/k8s/argocd/app-main-api.yaml
infra/k8s/argocd/app-aux-service.yaml


Each file tells Argo CD:

Where the manifests live in Git

What namespace to deploy into

Whether to auto-sync

Whether to self-heal

Example (simplified):

spec:
  source:
    repoURL: https://github.com/<your-repo>
    path: infra/k8s/apps/main-api
  destination:
    namespace: main-api
    server: https://kubernetes.default.svc
  syncPolicy:
    automated:
      prune: true
      selfHeal: true

3. How GitOps Works Here
Step 1: GitHub Actions updates manifests

Whenever we push a new image to ECR, GitHub Actions updates:

The Deployment manifest (new image tag)

The version ConfigMap

These changes are committed back to the repo.

Step 2: Argo CD detects the change

Argo CD monitors the repository:

If Git changes → Argo CD triggers a sync

If the cluster drifts → Argo CD restores the correct state

Step 3: Argo CD deploys automatically

Argo CD performs:

Rolling update

Health check

Status reporting

Sync confirmation

4. Accessing the Argo CD UI

After installation:

kubectl -n argocd port-forward svc/argocd-server 8080:443


Then open:

https://localhost:8080


Retrieve the initial admin password:

kubectl -n argocd get secret argocd-initial-admin-secret \
  -o jsonpath="{.data.password}" | base64 -d