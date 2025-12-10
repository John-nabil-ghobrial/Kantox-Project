1. Preparing AWS with Terraform

Navigate to the Terraform folder:

cd infra/terraform

Apply the infrastructure:
terraform init
terraform plan
terraform apply


This will create:

IAM Role for GitHub OIDC

IRSA roles for aux-service and the CSI driver

IAM role for Cluster Autoscaler

(Optional) EKS cluster and node groups

Once Terraform finishes, your AWS environment is ready for Kubernetes deployment.

2. Connecting to the EKS Cluster

If you provisioned the cluster using Terraform:

aws eks update-kubeconfig --name Kantox --region us-west-1


Verify the connection:

kubectl get nodes


You should see all your worker nodes listed.

3. Install Argo CD

Argo CD handles GitOps deployment for this project.

Apply the Kustomize package:

kubectl apply -k infra/k8s/argocd/


Wait for the pods to start:

kubectl get pods -n argocd


Retrieve the admin password:

kubectl -n argocd get secret argocd-initial-admin-secret \
  -o jsonpath="{.data.password}" | base64 -d


Expose Argo CD locally:

kubectl port-forward svc/argocd-server -n argocd 8080:443


Open:

https://localhost:8080

4. Deploy the Applications (GitOps)

Argo CD Applications are located under:

infra/k8s/argocd/


They define how the two services (main-api and aux-service) should be deployed.

Argo CD will automatically:

Sync the manifests

Deploy pods

Manage rollouts

Keep cluster state aligned with Git

You can watch the pods come online:

kubectl get pods -n main-api
kubectl get pods -n aux-service


Expected pods:

main-api Deployment

aux-service Deployment

Both with HPAs and Secrets mounted

5. Install the Secret Store CSI Driver

helm repo add secrets-store-csi-driver https://kubernetes-sigs.github.io/secrets-store-csi-driver/charts
helm install csi secrets-store-csi-driver/secrets-store-csi-driver -n kube-system

6. Validate Secrets Injection
kubectl get secret -n main-api
kubectl get secret -n aux-service


You should see:

kontox-secret

This component allows Kubernetes to load secrets directly from AWS Secrets Manager.

7. Install the Cluster Autoscaler

If autoscaling is needed:

kubectl apply -f infra/terraform/cluster-autoscaler/cluster-autoscaler.yaml


The IAM for autoscaler is already handled by Terraform.

Verify it is running:

kubectl get pods -n kube-system | grep autoscaler

8. install Mertic server 

9. Run the Monitoring Stack

Deploy Prometheus & Grafana:

helm install monitoring \
  prometheus-community/kube-prometheus-stack \
  -n monitoring


This gives full visibility into:

CPU/Memory

HPA decisions

Pod performance

Node health

10. Test the Application

Forward the main-api service:

kubectl port-forward -n main-api deploy/main-api 8080:8000


Examples:

curl http://localhost:8080/health
curl http://localhost:8080/buckets
curl http://localhost:8080/parameters
curl http://localhost:8080/parameters/myParam


All responses should include:

mainApiVersion

auxServiceVersion

The actual data from AWS or aux-service

Full testing documentation:
docs/api-testing.md

11. Summary

By following this guide, you will:

Provision AWS infrastructure with Terraform

Connect to EKS

Install Argo CD

Deploy both microservices using GitOps

Configure secrets with AWS Secrets Manager

Enable autoscaling

Optional: install monitoring stack

Validate the application using curl commands

This deployment flow is clean, automated, and ready for real-world usage.