Monitoring – Prometheus & Grafana (Optional Requirement)

Although monitoring is listed as optional in the challenge, this project includes a clean and extensible design for adding observability into the EKS cluster.
The goal is to ensure that you can easily monitor:

Cluster health

Pod resource usage

Node performance

Application-level metrics

Autoscaling behavior

This setup follows common patterns used in production Kubernetes environments.

1. Monitoring Namespace

All monitoring components are organized under:

infra/k8s/monitoring/


This keeps observability separated from application workloads and makes the system easier to maintain.

A simple namespace file is provided:

apiVersion: v1
kind: Namespace
metadata:
  name: monitoring


This ensures that monitoring tools remain isolated and follow best practices.

2. Recommended Monitoring Stack

For Kubernetes, the industry standard monitoring tools are:

✔ Prometheus

Collects cluster and application metrics.

✔ Grafana

Dashboard visualization.

✔ Node Exporter

Provides node-level CPU, memory, and disk metrics.

✔ Kube-State-Metrics

Exposes cluster object metrics (Deployments, Pods, HPAs, etc.)

✔ Alertmanager (optional)

Handles alerting rules.

Although not required for the challenge, having a defined structure shows readiness for production workloads.

3. Installing the Monitoring Stack

The recommended approach is to use the kube-prometheus-stack Helm chart, which includes all tools in a single bundle.

Installation steps:

helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm repo update

helm install monitoring \
  prometheus-community/kube-prometheus-stack \
  -n monitoring


This chart automatically deploys:

Prometheus operator

Prometheus server

Grafana

Node exporter

Kube-state-metrics

Required CRDs

This is the most common and widely supported monitoring setup for EKS.

4. Accessing Grafana

After installation, you can forward the Grafana service port:

kubectl port-forward -n monitoring svc/monitoring-grafana 3000:80


Then open in your browser:

http://localhost:3000


Default credentials:

User: admin

Password: prom-operator
(or retrieved dynamically if overridden)

Grafana automatically imports several dashboards for:

Node performance

Workload performance

Kubernetes control plane

Pod CPU/Memory usage

HPA behavior

5. Why Monitoring Matters

Even though this challenge does not require operational metrics, monitoring is still an important part of any EKS deployment.

Monitoring gives visibility into:

Pod resource saturation

Cluster autoscaler scaling events

Failing deployments

HPA scaling decisions

API performance

Memory leaks

Network bottlenecks

Including this optional section demonstrates understanding of production-readiness.